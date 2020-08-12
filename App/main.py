"""In charge of the launch of the program.
Call all the elements of the program in an orchestrated manner.
"""

from Model.Manager.db_manager import DBManager
from Model.Manager.entity_manager import EntityManager
from Model.Manager.api_manager import APIManager

from Controller.cli_controller import CLIController


class Main:

    def __init__(self):

        # create the managers
        self.db_manager = DBManager()
        self.entity_manager = EntityManager(self.db_manager)
        self.api_manager = APIManager()

        # create the controllers
        self.controller = CLIController()

        # create the interface
        self.controller.new_session()
