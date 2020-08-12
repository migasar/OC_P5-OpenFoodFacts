"""In charge of the manipulation of the content of the database.
This module is a layer which handle the interactions,
between the program, its objects and the database.
"""

from mysql.connector import Error

from Model.Entity.product import Product
from Model.Entity.category import Category
from Model.Entity.store import Store
from Model.Manager.db_manager import DBManager


class EntityManager:
    """Handle the interactions with the content of the database.
    The variable database is an instance of the class DBManager.
    """

    def __init__(self, db=DBManager()):
        self.db = db
        self.connection = db.connection

    @staticmethod
    def create_instance(entity, **attributes):
        """Create an instance of an entity.
        Generic method to create an instance of product, category or store
        from elements retrieved from the API or from the DB.
        'entity' is a string, which gives the name of the entity
         to instanciate: Product, Category, or Store
        'entity' is not used directly, but as a key of class_register
        (because we can't use a string with the name of a class
         to instanciate this class)
        '**attributes' is a dictionary, which can contain 2 types of items:
          - the attributes of the instanciation
          - the elements for a recursive call to create_instance()
        """

        # Register of the classes callable by the method:
        class_register = {
            'favorite_product': Product,
            'product': Product,
            'category': Category,
            'store': Store
        }

        # loop over the dictionary to review the names of the attributes
        # to cluster all the denominations of id_product in the db
        # and to normalize them to id_product for the creation of instance
        if 'id_substitute_product' in attributes.keys():
            attributes['id_product'] = attributes.pop('id_substitute_product')

        # loop over the dictionary to define the use of the pair (key, value)
        for key, value in attributes.items():

            if key in class_register and type(value) is str:
                # the item is a long string of multiple categories or stores

                instance_list = []
                # split this long string in one string per entity
                for val in value.split(','):

                    # try to create an instance for each 'category' or 'store'
                    try:
                        # if the key is in the register,
                        # it means that its values can be instanciated
                        instance = class_register[key](name=str(val).strip())

                        if instance.name == "":
                            # discard the instance, if the name is missing
                            raise KeyError
                        elif "'" in instance.name:
                            # discard the instance, if the name contains quotes
                            # to simplify the construction of sql queries
                            raise KeyError

                    except KeyError:
                        continue

                    else:
                        # finallly, add the instance to the list
                        instance_list.append(instance)

                # update this value in the dictionary:
                # replace the long string with the list of instances
                attributes[key] = instance_list

        # use the value in the register to instanciate the class
        return class_register[entity](**attributes)

    def flatten_list(self, listing, components=None):
        """Serialize a nested list (of an unknown depth).
        It returns a flattened list,
        with the same elements (they are all brought at the same level).
        This method is used by the method insert_load(),
        on the result from the method create_query_insert().
        """

        atoms = [] if components is None else components

        for element in listing:
            # if the function encounters another sub-level,
            # it launch a recursive call to bring its elements forward
            if type(element) is list:
                self.flatten_list(element, atoms)
            else:
                atoms.append(element)

        return atoms

    @staticmethod
    def format_row_parameters(row_keys, row_values):
        # format the parameters as cleaned strings

        if (len(row_keys) or len(row_values)) == 1:
            single_row_key = str("'" + str(row_keys[0]) + "'")
            row_keys = str("(" + single_row_key + ")").replace("'", "")
            single_row_value = str("'" + str(row_values[0]) + "'")
            row_values = str("(" + single_row_value + ")")

        else:
            row_keys = str(tuple(row_keys)).replace("'", "")
            row_values = str(tuple(row_values))

        return row_keys, row_values

    def format_query_insert_load(self, entity, parent=None):
        """Create a string used as a query.
        from a formatted string and the variables used as parameters
        """

        # repository for the formatted queries
        children = []

        # set the parameters
        table_name = entity.__class__.__name__.lower()
        row_keys = []
        row_values = []

        # unpack the attributes of the entity
        for item in entity.get_items():
            attribute_key = item[0]
            attribute_value = item[1]

            if attribute_value is None:
                # discard the attributes without value
                pass

            elif type(attribute_value) is list:
                # launch a recursive call,
                # if the attribute is a repository of other instances
                for child in attribute_value:
                    children.append(
                        self.format_query_insert_load(child, entity)
                    )

            else:
                # collect the variables needed to create a row of data
                row_keys.append(attribute_key)
                row_values.append(attribute_value)

        # format the parameters as cleaned strings inside parenthesis
        row_keys, row_values = self.format_row_parameters(row_keys, row_values)

        # format the query
        query = (
            f"INSERT INTO {table_name} "
            f"  {row_keys} "
            f"  VALUES {row_values} "
            f"ON DUPLICATE KEY UPDATE "
            f"  id_{table_name} = LAST_INSERT_ID(id_{table_name}); "
            f"SET @id_{table_name} = LAST_INSERT_ID() "
        )

        # depending of the instance,
        # modify the query to add a request for the tables of associations
        if parent is not None:
            parent_name = parent.__class__.__name__.lower()
            query_tail = (
                f"; "
                f"INSERT IGNORE INTO {table_name}_{parent_name} "
                f"  (id_{table_name}, id_{parent_name}) "
                f"  VALUES (@id_{table_name}, @id_{parent_name}) "
            )
            query += query_tail

        # finally, the formatted query is added to the list of 'queries'
        children.append(query)

        return children

    def insert_load(self, payload):
        """Insert rows in a table.
        The method 'insert_load' orchestrates the call to the methods
        to create a query to insert a row in the db
        for each instance in 'payload.'
        The result will be a list of queries,
        which will be coerced in a long string,
        and then sent to the db.
        """

        # repository for the formatted queries
        queries = []

        # create queries from the objects in payload
        if type(payload) is list:
            # create a query for each instance of the list
            for instance in payload:
                queries.append(
                    self.format_query_insert_load(instance)
                )

        else:
            # in case, the payload is a single instance
            queries.append(
                self.format_query_insert_load(payload)
            )

        # unpack the nested list of queries
        request = self.flatten_list(queries)
        # reverse back the order of the stack of queries
        # (because the method flatten_list is a recursive function,
        # which put upside-down the order of elements in the nested list)
        request.reverse()

        # try to execute every query in one command to the db
        try:
            # join in an unique string, all the elements of the list of queries
            statement = str('; '.join(request))

            cursor = self.connection.cursor()
            for _ in (cursor.execute(statement, multi=True)):
                # yield each statement in the generator expression,
                # with the parameter 'multi=True'
                continue

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"The error '{e}' occurred")

    def insert_row(self, table_anchor, row_keys, row_values):

        # format the parameters as cleaned strings inside parenthesis
        row_keys, row_values = self.format_row_parameters(row_keys, row_values)

        # format the query
        query = (
            f"INSERT IGNORE INTO {table_anchor} "
            f"  {row_keys} "
            f"  VALUES {row_values} ;"
        )

        # execute the query
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"The error '{e}' occurred")

    def select_row(self, table_anchor, selection, **claims):
        """Retrieve rows from the db and bring them back as instances.
        table_anchor: the name of the table where is the row that we want
        selection: the columns with the values of the row that we want
        **claims: optional components to build the query to the db
        """

        # query
        claim = []

        # SELECT
        claim_select = f"SELECT DISTINCT "

        headers = [str(head) for head in selection]
        columns = [f"{table_anchor}.{col}" for col in headers]
        selection = ', '.join([c for c in columns])

        claim_select += f"{selection}  "
        claim.append(claim_select)

        # FROM
        claim_from = f"FROM {table_anchor} "
        claim.append(claim_from)

        # JOIN
        if 'join' in claims:

            # join parameters:
            table_adjunct = claims['join']['table_adjunct']
            row_key_adjunct = claims['join']['row_key_adjunct']
            row_key_anchor = claims['join']['row_key_anchor']

            # join segment:
            claim_join = (
                f"INNER JOIN {table_adjunct} "
                f"ON {table_adjunct}.{row_key_adjunct} "
                f"= {table_anchor}.{row_key_anchor} "
            )

            claim.append(claim_join)

        # WHERE
        if 'where' in claims:

            # where parameters:
            table_adjunct = claims['where']['table_adjunct']
            row_key = claims['where']['row_key']

            if type(claims['where']['row_value']) is int:
                single_value = "('" + str(claims['where']['row_value']) + "')"
                row_value = single_value

            elif type(claims['where']['row_value']) is list and len(
                    claims['where']['row_value']
            ) == 1:
                single_list_value = (
                    "('" + str(claims['where']['row_value'][0]) + "')"
                )
                row_value = single_list_value

            else:
                multiple_values = str(tuple(claims['where']['row_value']))
                row_value = multiple_values

            # where segment:
            claim_where = (
                f"WHERE {table_adjunct}.{row_key} "
                f"IN {row_value} "
            )

            claim.append(claim_where)

        # ORDER
        if 'order' in claims:
            claim_order = f"ORDER BY {claims['order']} "
            claim.append(claim_order)

        # punctuation to indicate the end of the query
        claim_tail = ";"
        claim.append(claim_tail)

        # format the query
        statement = str(' '.join(claim))

        # execute the query
        try:
            cursor = self.connection.cursor()
            cursor.execute(statement)

            records = cursor.fetchall()
            cursor.close()

            # transform the rows in instances and return them in a list
            instances_list = []
            for record in records:

                # retrieve the elements from each record,
                # that will serve as values for the next method
                values = list(record)
                attrs = dict(zip(headers, values))

                # create an instance with elements found in this row of th db
                instances_list.append(
                    self.create_instance(table_anchor, **attrs)
                )

            return instances_list

        except Error as e:
            print(f"The error '{e}' occurred")
