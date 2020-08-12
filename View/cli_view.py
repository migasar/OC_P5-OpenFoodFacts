"""Manage the display of the program on the terminal."""


class CLIView:
    """Regroup methods to display elements of the program on a terminal."""

    # Input command
    @staticmethod
    def input_request():
        """Display the input to receive the command from the user."""

        command = input("Entrez le numéro de la prochaine action : ")
        print()

        return command

    @staticmethod
    def input_failure():
        """Display a text explaining that the command didn't work."""

        print("Désolé, nous ne comprenons pas votre commande. ")

    # Descriptions
    @staticmethod
    def text_introduction():
        """Display a text explaining the purpose of the program."""

        print("""
--------------------------------------
Bienvenue sur l'application Pur Beurre
--------------------------------------
Pour vous aider à améliorer votre alimentation, 
nous allons essayer de vous proposer
un substitut plus sain à l'aliment que vous nous indiquerez.
""")

    @staticmethod
    def text_closing():
        """Display an anouncement indicating that the program is closing."""

        print("Merci d'avoir utilisé notre programme.")

    @staticmethod
    def text_new_db():
        """Display an anouncement indicating that the program is closing."""

        print("La base de donnée est relancée.")

    @staticmethod
    def text_category():
        """Display a text demanding to the user to choose a category."""

        print("Sélectionnez la catégorie.")

    @staticmethod
    def text_product():
        """Display a text demanding to the user to choose a product."""

        print("Sélectionnez un aliment.")

    @staticmethod
    def text_substitute():
        """Display the possibility to select one of the substitutes."""

        print("Sélectionnez le substitut qui vous intéresse. ")

    @staticmethod
    def text_no_substitute():
        """Display a text announcing that no substitute was found."""

        print("Nous n'avons pas trouvé de substitut à cet aliment.")

    @staticmethod
    def text_no_favorite():
        """Display a text announcing that no product have been saved so far."""

        print("Vous n'avez pas encore sauvegardé d'aliments.")

    @staticmethod
    def title_opening():
        """Display the title of this step to clarify the flow of the program."""

        print("""
MENU PRINCIPAL
--------------""")

    @staticmethod
    def title_category():
        """Display the title of this step to clarify the flow of the program."""

        print("""
CATEGORIES
----------""")

    @staticmethod
    def title_product():
        """Display the title of this step to clarify the flow of the program."""

        print("""
ALIMENTS
--------""")

    @staticmethod
    def title_substitute():
        """Display the title of this step to clarify the flow of the program."""

        print("""
SUBSTITUTS
----------""")

    @staticmethod
    def title_saving():
        """Display the title of this step to clarify the flow of the program."""

        print("""
SELECTION
---------""")

    @staticmethod
    def title_favorite():
        """Display the title of this step to clarify the flow of the program."""

        print("""
FAVORIS
-------""")

    @staticmethod
    def commands_explanation():
        """Display the actions available to the user."""

        print("Pour choisir une action, indiquez son numéro.")

    # Commands for sidesteps
    @staticmethod
    def command_closing():
        """Display the command used to end the program."""

        print("X. Quitter le programme. ")

    @staticmethod
    def command_renew_db():
        """Display the command used to recreate the database."""

        print("0. Reconstruire la base de données. ")

    @staticmethod
    def command_backstep():
        """Display the commands used to return to the previous step."""

        print("0. Revenir à l'étape précédente. ")

    @staticmethod
    def command_newstep():
        """Display the commands used to return to the previous step."""

        print("0. Revenir au menu principal. ")

    # Commands pre-defined
    @staticmethod
    def command_opening():
        """Display the commands available to the user."""

        print("1. Quel aliment souhaitez-vous remplacer ? ")
        print("2. Retrouver vos alments substitués. ")

    @staticmethod
    def command_saving():
        """Display the option to save a substitute as favorite."""

        print("1. Revenir au menu principal. ")
        print("2. Sauvegarder cet aliment dans vos favoris. ")

    # Commands from selection
    @staticmethod
    def display_category(roster):
        """Display all the categories in the database."""

        for category in roster:
            print(f"{category.id_category}. {category.name} ")

    @staticmethod
    def display_product(roster):
        """Display the products associated to a variable.
        It can be all the products inside the selected category,
        or it can be all the substitutes of a specific product.
        """

        for product in roster:
            print(
                f"{product.id_product}. {product.name} \
| nutriscore : {product.nutriscore}"
            )

    @staticmethod
    def display_result(roster):
        """Display the products with their details."""

        for product in roster:
            print(f"""- {product.name} :
        nutriscore : {product.nutriscore}
        url : {product.url}
        catégories : {', '.join([cat.name for cat in product.category])}
        magasins : {', '.join([
                shop.name 
                if shop is not None else 'aucun' 
                for shop in product.store
            ])}
""")
