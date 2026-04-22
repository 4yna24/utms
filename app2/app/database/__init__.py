from flask import current_app

from .adapters import SQLAlchemyDatabaseAdapter, SQLAlchemyUserDataService


def init_database_interfaces(app):
    database_interface = SQLAlchemyDatabaseAdapter()
    user_data_interface = SQLAlchemyUserDataService(database_interface)

    app.extensions['database_interface'] = database_interface
    app.extensions['user_data_interface'] = user_data_interface


def get_database_interface():
    return current_app.extensions['database_interface']


def get_user_data_interface():
    return current_app.extensions['user_data_interface']
