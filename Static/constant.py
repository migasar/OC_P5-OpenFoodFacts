"""Regroup the constants of the program: settings, parameters, etc..."""

import os


# address of connection to the API of OpenFoodFacts
OFF_URL = 'https://fr.openfoodfacts.org/cgi/search.pl'

# parameters for the connection to the API of OpenFoodFacts
API_ACTION = 'process'
API_SORT_BY = 'unique_scans_n'
API_JSON = 'true'
API_PARAMETERS = {
    'action': API_ACTION,
    'sort_by': API_SORT_BY,
    'json': API_JSON
}

# public parameters for the database
DB_NAME = 'purbeurre'

# parameters to set the paths inside the project structure
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'Static', 'schema_purbeurre.sql')


def get_path(*args):
    """Create a path to any component of the project."""
    return os.path.join(PROJECT_ROOT, *args)
