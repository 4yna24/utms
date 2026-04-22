from app import db
from app.models import User

from .interfaces import DatabaseInterface, UserDataInterface


class SQLAlchemyDatabaseAdapter(DatabaseInterface):
    def execute_query(self, action_name, payload=None):
        payload = payload or {}

        if action_name == 'find_user_by_email_role':
            return User.query.filter_by(
                email=payload['email'],
                role=payload['role'],
            ).first()

        if action_name == 'create_user':
            user = User(email=payload['email'], role=payload['role'])
            user.set_password(payload['password'])
            db.session.add(user)
            db.session.commit()
            return user

        raise ValueError(f'Unknown database action: {action_name}')


class SQLAlchemyUserDataService(UserDataInterface):
    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def find_by_email_role(self, email, role):
        return self.database_adapter.execute_query(
            'find_user_by_email_role',
            {'email': email, 'role': role},
        )

    def create_user(self, email, password, role):
        return self.database_adapter.execute_query(
            'create_user',
            {'email': email, 'password': password, 'role': role},
        )
