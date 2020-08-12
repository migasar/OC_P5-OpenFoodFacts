""" Create an object 'Product' to carry the data of the products. """


class Product:
    """Create an object describing one product."""

    def __init__(self, **kwargs):

        # Predefine attributes with default values
        self.id_product = None
        self.name = None
        self.nutriscore = None
        self.url = None
        self.category = None
        self.store = None

        # Get a list of all predefined values directly from __dict__
        whitelist = list(self.__dict__.keys())

        # Update __dict__ for keys that have been predefined
        for key, value in kwargs.items():
            if key in whitelist:
                setattr(self, key, value)
            else:
                raise ValueError("Unexpected kwarg value")

    def __repr__(self):
        """Create a more usable representation of the object.
        The idea with this representation is to call a string similar
        to the command used to instanciate the object.
        """

        values_list = [
            ("'" + str(v) + "'")
            for (k, v) in self.__dict__.items()
            if v is not None
        ]

        return (f"{self.__class__.__name__}"
                f"({', '.join([v for v in values_list])})")

    def get_items(self):
        """Create a list of tuples
        with the name and the value of each attribute (which are not empty).
        """

        return [
            (k, v)
            if type(v) is not list
            else (k, [x for x in v])
            for (k, v) in self.__dict__.items()
            if v is not None
        ]
