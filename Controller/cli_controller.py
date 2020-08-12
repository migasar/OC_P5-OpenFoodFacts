"""Manage the flow of the program, and the interactions of its components."""

from Model.Manager.entity_manager import EntityManager
from Model.Manager.api_manager import APIManager
from View.cli_view import CLIView


class CLIController:
    """Pilot the flow of the program.
    It orchestrate the interactions between the main elements of the program:
     - the models
     - the views
     - the input of the user
    """

    # Class variable (register of all the phases in the flow of the program):
    steps = {
            'closing': 0,
            'opening': 1,
            'category': 2,
            'product': 3,
            'substitute': 4,
            'saving': 5,
            'favorite': 6
    }

    def __init__(self):

        self.entity_manager = EntityManager()
        self.api_manager = APIManager()
        self.view = CLIView()

        self.phase = self.steps['opening']  # the actual phase in the program
        self.input = None  # user input
        self.choices = {
                'catalog_category': [],
                'opt_category': [],
                'roster_product': [],
                'opt_product': [],
                'roster_substitute': [],
                'opt_substitute': [],
                'roster_favorite': []
        }  # results based on user input

    # structure
    def create_database(self):
        """Call the elements to create the database,
        and to retrieve the data to fill it.
        """

        # build the database skeleton
        self.entity_manager.db.build_database()

        # call the API
        self.api_manager.get_load()

        # download the data (from the API to the DB)
        self.api_manager.download_data()

    def fulfill_database(self):
        """Replenish the db if it is empty."""

        # interrogate the db to see if it is empty
        production = [
            p for p in self.entity_manager.select_row(
                table_anchor='product',
                selection=['id_product', 'name']
            )
        ]

        # replenish the db
        if not production:
            # call the API
            self.api_manager.get_load()
            # download the data (from the API to the DB)
            self.api_manager.download_data()

    def get_products(
            self,
            category=None,
            substitute=None,
            result=None,
            favorites=None
    ):
        """Interrogate the db to get a list of products.
        """

        if category is not None:
            # get the products associated to a category

            claims_product = {
                    'order': 'id_product',
                    'join': {
                            'table_adjunct': 'category_product',
                            'row_key_adjunct': 'id_product',
                            'row_key_anchor': 'id_product'
                    },
                    'where': {
                            'table_adjunct': 'category_product',
                            'row_key': 'id_category',
                            'row_value': category.id_category
                    }
            }

            return self.entity_manager.select_row(
                table_anchor='product',
                selection=['id_product', 'name', 'nutriscore', 'url'],
                **claims_product
            )

        elif substitute is not None:
            # get the substitutes associated to a product

            # get all the categories of the selected product
            claims_procats = {
                'order': 'id_category',
                'join': {
                    'table_adjunct': 'category_product',
                    'row_key_adjunct': 'id_category',
                    'row_key_anchor': 'id_category'
                },
                'where': {
                    'table_adjunct': 'category_product',
                    'row_key': 'id_product',
                    'row_value': substitute.id_product
                }
            }
            roster_category = self.entity_manager.select_row(
                table_anchor='category',
                selection=['id_category', 'name'],
                **claims_procats
            )

            # fill the attribute category of this product
            substitute.category = roster_category

            # create a list of id numbers to use as value for the next method
            register_id_roster_cat = [r.id_category for r in roster_category]

            # get all the products of the roster of categories
            claims_substitute = {
                'order': 'id_product',
                'join': {
                    'table_adjunct': 'category_product',
                    'row_key_adjunct': 'id_product',
                    'row_key_anchor': 'id_product'
                },
                'where': {
                    'table_adjunct': 'category_product',
                    'row_key': 'id_category',
                    'row_value': register_id_roster_cat
                }
            }
            roster_substitute = self.entity_manager.select_row(
                table_anchor='product',
                selection=['id_product', 'name', 'nutriscore', 'url'],
                **claims_substitute
            )

            # remove the selected product from the list of its substitutes
            for sub in roster_substitute:
                # search for the selected product in the list of substotutes
                if sub.id_product == substitute.id_product:
                    # try to remove it from the list
                    try:
                        roster_substitute.remove(sub)
                    except ValueError:
                        continue

            return roster_substitute

        elif result is not None:
            # add the categories and the stores to the instance of a product

            # get all the categories of the product result
            result_cats = self.get_categories(product=result)
            result.category = result_cats

            # get all the stores of the product result
            result_shops = self.get_stores(product=result)
            result.store = result_shops

            # return the product result after adding all the details
            return result

        elif favorites is not None:
            # get all the products saved as favorites

            favorite_list = []
            for id_fav in favorites:

                claims_fav = {
                    'where': {
                        'table_adjunct': 'product',
                        'row_key': 'id_product',
                        'row_value': id_fav
                    }
                }
                fav = self.entity_manager.select_row(
                    table_anchor='product',
                    selection=['id_product', 'name', 'nutriscore', 'url'],
                    **claims_fav
                )

                favorite_list.append(self.get_products(result=fav[0]))

            return favorite_list

        else:
            # get all the products in the db
            claims_product = {
                'order': 'id_product',
            }

            return self.entity_manager.select_row(
                table_anchor='product',
                selection=['id_product', 'name', 'nutriscore', 'url'],
                **claims_product
            )

    def get_categories(self, product=None):
        """Interrogate the db to get a list of categories."""

        if product is None:
            # get all the categories in the db
            claims_category = {
                'order': 'id_category'
            }

        else:
            # get the categories associated to the product
            claims_category = {
                'order': 'id_category',
                'join': {
                    'table_adjunct': 'category_product',
                    'row_key_adjunct': 'id_category',
                    'row_key_anchor': 'id_category'
                },
                'where': {
                    'table_adjunct': 'category_product',
                    'row_key': 'id_product',
                    'row_value': product.id_product
                }
            }

        return self.entity_manager.select_row(
            table_anchor='category',
            selection=['id_category', 'name'],
            **claims_category
        )

    def get_stores(self, product=None):
        """Interrogate the db to get a list of stores."""

        if product is None:
            # get all the categories in the db
            claims_store = {
                'order': 'id_store'
            }

        else:
            # get the categories associated to the product
            claims_store = {
                'order': 'id_store',
                'join': {
                    'table_adjunct': 'store_product',
                    'row_key_adjunct': 'id_store',
                    'row_key_anchor': 'id_store'
                },
                'where': {
                    'table_adjunct': 'store_product',
                    'row_key': 'id_product',
                    'row_value': product.id_product
                }
            }

        return self.entity_manager.select_row(
            table_anchor='store',
            selection=['id_store', 'name'],
            **claims_store
        )

    # flow
    def new_session(self):
        """Call the elements to start the program"""

        self.fulfill_database()
        self.view.text_introduction()
        self.action_triage()

    def action_triage(self):
        """Orchestrate the flow of the program.
        It selects the next methods to call.
        The methods are chosen in function
        of the current phase of the program
        and the command sent by the user.
        """

        # 0. closing step:
        if self.phase == self.steps['closing']:
            self.step_closing()

        # 1. opening step
        elif self.phase == self.steps['opening']:
            self.step_opening()

        # 2. category step
        elif self.phase == self.steps['category']:
            self.step_category()

        # 3. product step
        elif self.phase == self.steps['product']:
            self.step_product()

        # 4. substitute step
        elif self.phase == self.steps['substitute']:
            self.step_substitute()

        # 5. saving step
        elif self.phase == self.steps['saving']:
            self.step_saving()

        # 6. favorite step
        elif self.phase == self.steps['favorite']:
            self.step_favorite()

    def action_call(self):
        """Ask for an action to the user, and treat its command.
        Verify which command was sent by the user, and call its methods.
        """

        # 1. opening step
        if self.phase == self.steps['opening']:

            # print the text describing the step
            self.view.title_opening()
            self.view.commands_explanation()

            # print the commands available at this step
            self.view.command_closing()  # 'X' command
            self.view.command_renew_db()  # '0' command
            self.view.command_opening()  # 1-2 commands

        # 2. category step
        elif self.phase == self.steps['category']:

            # print the text describing the step
            self.view.title_category()
            self.view.commands_explanation()

            # print the commands available at this step
            self.view.text_category()
            self.view.command_closing()  # 'X' command
            self.view.command_backstep()  # '0' command
            self.view.display_category(self.choices['catalog_category'])  # n commands

        # 3. product step
        elif self.phase == self.steps['product']:

            # print the text describing the step
            self.view.title_product()
            self.view.commands_explanation()

            # print the commands available at this step
            self.view.text_product()
            self.view.command_closing()  # 'X' command
            self.view.command_backstep()  # '0' command
            self.view.display_product(self.choices['roster_product'])  # n commands

        # 4. substitute step
        elif self.phase == self.steps['substitute']:

            # print the text describing the step
            self.view.title_substitute()
            self.view.commands_explanation()

            # print the commands available at this step
            self.view.text_substitute()
            self.view.command_closing()  # 'X' command
            self.view.command_backstep()  # '0' command
            self.view.display_product(self.choices['roster_substitute'])  # n commands

        # 5. saving step
        elif self.phase == self.steps['saving']:

            # print the text describing the step
            self.view.title_saving()
            self.view.commands_explanation()

            # print the commands available at this step
            self.view.command_closing()  # 'X' command
            self.view.command_backstep()  # '0' command
            self.view.command_saving()  # 1-2 commands
            print()
            self.view.display_result(self.choices['opt_substitute'])

        # 6. favorite step
        elif self.phase == self.steps['favorite']:

            # print the text describing the step
            self.view.title_favorite()
            self.view.commands_explanation()

            # print the commands available at this step
            self.view.command_closing()  # 'X' command
            self.view.command_newstep()  # '0' command
            print()
            self.view.display_result(self.choices['roster_favorite'])

        # get the input from the user and test if it is a valid option
        self.input = None
        self.input = self.view.input_request()

        self.check_input()

        # flag input failure
        if self.input is None:
            self.view.input_failure()
            return self.action_triage()
        else:
            return self.input

    # input
    def check_input(self):
        """Review the input from the user.
        Ensure its validity, and then decide of the use of the input."""

        if type(self.input) is str:

            try:
                # check if the input can be coerced in an integer
                int(self.input)

            except ValueError:
                # check if the input is the closure command
                if self.input.lower() == 'x':
                    # close the program
                    self.phase = self.steps['closing']
                    self.action_triage()

                # concludes that the input is a wrong command
                else:
                    self.input = None

            else:
                # coerce the input in an integer if possible
                self.input = int(self.input)

        else:
            # concludes that the input is of the wrong type
            self.input = None

        return self.input

    def clear_choices(self):
        """Restore the default values in the dictionnary self.choices"""

        for key, value in self.choices.items():
            self.choices[key] = []

        return self.choices

    # steps
    def step_closing(self):
        """Orchestrate the actions that happen in this step."""

        # announce the end of the program and close it
        self.view.text_closing()
        self.entity_manager.db.close_connection()
        exit()

    def step_opening(self):
        """Orchestrate the actions that happen in this step."""

        # reset the dictionnary self.choices
        self.clear_choices()

        # call the user input for this step
        self.action_call()

        # recreate the db
        if self.input == 0:
            self.view.text_new_db()
            self.create_database()
            self.action_triage()

        # go to category step
        elif self.input == 1:
            self.phase = self.steps['category']
            self.action_triage()

        # go to favorite step
        elif self.input == 2:
            self.phase = self.steps['favorite']
            self.action_triage()

        # flag input failure
        else:
            self.view.input_failure()
            return self.action_triage()

    def step_category(self):
        """Orchestrate the actions that happen in this step."""

        # interrogate the db to get a list of all the categories
        self.choices['catalog_category'] = self.get_categories()

        # create a list of id numbers to test if the input is an error
        register_id_category = [
                c.id_category for c in self.choices['catalog_category']
        ]

        # display the categories and propose to select one
        self.action_call()

        # rollback to the previous step
        if self.input == 0:
            self.phase = self.steps['opening']
            self.choices['catalog_category'] = []
            self.action_triage()

        # pick a category and go to product step
        elif self.input in register_id_category:

            for cat in self.choices['catalog_category']:
                if self.input == cat.id_category:
                    self.choices['opt_category'].append(cat)

            self.phase = self.steps['product']
            self.action_triage()

        # flag input failure
        else:
            self.view.input_failure()
            return self.action_triage()

    def step_product(self):
        """Orchestrate the actions that happen in this step."""

        # interrogate the db to get the products in the category
        self.choices['roster_product'] = self.get_products(
            category=self.choices['opt_category'][0])

        # create a list of id numbers to test if the input is an error
        register_id_product = [
                p.id_product for p in self.choices['roster_product']
        ]

        # display the products and propose to select one
        self.action_call()

        # rollback to the previous step
        if self.input == 0:
            self.phase = self.steps['category']
            self.choices['catalog_category'] = []
            self.choices['opt_category'] = []
            self.choices['roster_product'] = []
            self.action_triage()

        # pick a product and go to substitute step
        elif self.input in register_id_product:

            for prod in self.choices['roster_product']:
                if self.input == prod.id_product:
                    self.choices['opt_product'].append(prod)

            self.phase = self.steps['substitute']
            self.action_triage()

        # flag input failure
        else:
            self.view.input_failure()
            return self.action_triage()

    def step_substitute(self):
        """Orchestrate the actions that happen in this step.
        Interrogate the db to get a list of all the substitutes
        of the selected product
        by getting the products sharing at least one category.
        """

        # get all the substitutes to the product
        self.choices['roster_substitute'] = self.get_products(
            substitute=self.choices['opt_product'][0])

        # test if there is no substitute for this product
        if len(self.choices['roster_substitute']) == 0:
            # anounce to the user that the product has no substitute in the db
            self.view.text_no_substitute()
            self.phase = self.steps['opening']
            self.action_triage()

        # create a list of id numbers to test if the input is an error
        register_id_substit = [
                s.id_product for s in self.choices['roster_substitute']
        ]

        # display the substitutes and propose to select one
        self.action_call()

        # rollback to the previous step
        if self.input == 0:
            self.phase = self.steps['product']
            self.choices['roster_product'] = []
            self.choices['opt_product'] = []
            self.choices['roster_substitute'] = []
            self.action_triage()

        # pick a substitute and go to saving step
        elif self.input in register_id_substit:

            # search for the selected substitute in the list
            for sub in self.choices['roster_substitute']:
                if self.input == sub.id_product:

                    # return the substitute after adding all the details
                    self.choices['opt_substitute'].append(
                        self.get_products(result=sub)
                    )

            self.phase = self.steps['saving']
            self.action_triage()

        # flag input failure
        else:
            self.view.input_failure()
            return self.action_triage()

    def step_saving(self):
        """Orchestrate the actions that happen in this step."""

        # get an instance of the selected product
        # display the result and offer to save it in the favorites
        self.action_call()

        # rollback to the previous step
        if self.input == 0:
            self.phase = self.steps['substitute']
            self.choices['roster_substitute'] = []
            self.choices['opt_substitute'] = []
            self.action_triage()

        # return to the main menu
        elif self.input == 1:
            self.phase = self.steps['opening']
            self.action_triage()

        # save the substitute and go to favorite step
        elif self.input == 2:
            self.entity_manager.insert_row(
                    table_anchor='favorite_product',
                    row_keys=['id_base_product', 'id_substitute_product'],
                    row_values=[
                        self.choices['opt_product'][0].id_product,
                        self.choices['opt_substitute'][0].id_product
                    ]
            )

            self.phase = self.steps['favorite']
            self.action_triage()

        # flag input failure
        else:
            self.view.input_failure()
            return self.action_triage()

    def step_favorite(self):
        """Orchestrate the actions that happen in this step."""

        # get instances of all products saved as favorite

        # interrogate the db to get the id of the favorites
        roster_fav = [
            fav for fav in self.entity_manager.select_row(
                table_anchor='favorite_product',
                selection=['id_substitute_product']
            )
        ]
        roster_fav_id = [r.id_product for r in roster_fav]

        # test if there is no favorite yet
        if not roster_fav_id:
            # anounce to the user that no favorite has been saved in the db
            self.view.text_no_favorite()
            self.phase = self.steps['opening']
            self.action_triage()

        else:
            # interrogate the db to get the instances of the favorites
            self.choices['roster_favorite'] = self.get_products(
                favorites=roster_fav_id
            )

        # display the substitutes saved as favorites
        self.action_call()

        # return to the main menu
        if self.input == 0:
            self.phase = self.steps['opening']
            self.action_triage()

        # flag input failure
        else:
            self.view.input_failure()
            return self.action_triage()
