"""Handle the storage of the data.
From the creation of the database and its components,
to the insertion of the data in the database.
"""

import mysql.connector as mysql
from mysql.connector import Error

import Static.credential as credential
import Static.constant as constant


class Borg:
    """Metaclass to apply the Borg pattern to a subclass.
    It makes sure that there is only one instance of a class that is in use.
    The Borg pattern is an alternative to the Singleton.
    It doesn't really block the creation of over instances,
    but it ensures that all instances share state and behavior.
    The subclass behaves as if only the last created instance is callable,
    which gives the possibility to modify the instance.
    """

    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state


class DBManager(Borg):
    """Create the database or initiate its connection, if it already exists."""

    def __init__(
            self,
            host_name=None,
            user_name=None,
            user_password=None,
            db_name=None
    ):

        # ensure that only one instance of 'DBManager' is at play
        Borg.__init__(self)

        # default values for the parameters of the connection
        if host_name is None:
            host_name = credential.DB_HOST
        if user_name is None:
            user_name = credential.DB_USER
        if user_password is None:
            user_password = credential.DB_PASSWORD

        # parameters of the connection
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.db_name = db_name

        # initiate a connection to the server
        self.connection = self.set_connection()

        # initiate a connection to the db
        self.check_database()

    def set_connection(self):
        """Create a connection with MySQL server.
        If db_name is specified, create a connection specifically to a database.
        """

        try:
            # create a general connection to MySQL server
            if self.db_name is None:
                self.connection = mysql.connect(
                    host=self.host_name,
                    user=self.user_name,
                    passwd=self.user_password
                )

            # create a connection specifically to a database
            else:
                self.connection = mysql.connect(
                    host=self.host_name,
                    user=self.user_name,
                    passwd=self.user_password,
                    database=self.db_name
                )

        except Error as e:
            print(f"The error'{e}' occured")

        return self.connection

    def check_database(self, db_name=None):
        """Check if the database already exists.
        Otherwise, it calls the method build_database.
        """

        if db_name is None:
            db_name = constant.DB_NAME

        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")

        databs = cursor.fetchall()
        databases = [d[0] for d in databs]

        self.connection.commit()
        cursor.close()

        # create the db if it doesn't exist
        if db_name not in databases:
            self.build_database()

        # otherwise, set the connection to the db
        else:
            self.db_name = db_name
            self.connection = self.set_connection()

    def build_database(self, filepath=constant.SCHEMA_PATH):
        """Initiate the creation of the database.
        Take the path to a sql file as variable,
        and use the file as a schema to build the database.
        """

        # open the sql file as an object to pass its content to other methods
        with open(filepath, 'r') as f:
            sql_file = f.read()
            # delete all the end lines in the file
            sql_file = sql_file.replace("\n", "")
            # explicitly split every query inside the file
            sql_file = sql_file.split(';')

        # execute, one by one, every query from the schema

        cursor = self.connection.cursor()
        for line in sql_file:
            cursor.execute(line)

        self.connection.commit()
        cursor.close()

        # renew set_connection() to initiate a connection with the database
        self.db_name = constant.DB_NAME
        self.connection = self.set_connection()

        return self.connection

    def close_connection(self):
        """Close the connection with MySQL server."""

        try:
            self.connection.close()

        except Error as e:
            print(f"The error'{e}' occured")
