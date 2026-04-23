from pathlib import Path
import shutil

from flask import current_app
from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import User

from .interfaces import DatabaseControlInterface, DatabaseInterface, UserDataInterface


class SQLAlchemyDatabaseAdapter(DatabaseInterface, DatabaseControlInterface):
    def __init__(self):
        self.connected = False

    def execute_query(self, action_name, payload=None):
        payload = payload or {}

        if action_name == 'find_user_by_email_role':
            return User.query.filter_by(
                email=payload['email'],
                role=payload['role'],
            ).first()

        if action_name == 'find_user_by_id':
            return db.session.get(User, payload['user_id'])

        if action_name == 'create_user':
            if payload.get('check_user_validity', True):
                existing_user = User.query.filter_by(
                    email=payload['email'],
                    role=payload['role'],
                ).first()
                if existing_user:
                    return None

            user = User(email=payload['email'], role=payload['role'])
            user.set_password(payload['password'])
            try:
                db.session.add(user)
                db.session.commit()
                return user
            except IntegrityError:
                db.session.rollback()
                return None

        raise ValueError(f'Unknown database action: {action_name}')

    def safe_execute(self, action_name, payload=None):
        allowed_actions = {'find_user_by_email_role', 'find_user_by_id', 'create_user'}
        if action_name not in allowed_actions:
            raise PermissionError(f'Action not allowed: {action_name}')
        return self.execute_query(action_name=action_name, payload=payload)

    def connect(self):
        self.connected = True

    def disconnect(self):
        if db.session.is_active:
            db.session.remove()
        self.connected = False

    def backup(self):
        database_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not database_uri.startswith('sqlite:///'):
            return None

        db_relative = database_uri.removeprefix('sqlite:///')
        instance_path = Path(current_app.instance_path)
        source = instance_path / db_relative

        if not source.exists():
            return None

        backup_path = source.with_suffix('.bak')
        shutil.copy2(source, backup_path)
        return str(backup_path)


class SQLAlchemyUserDataService(UserDataInterface):
    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def find_by_email_role(self, email, role):
        return self.database_adapter.safe_execute(
            'find_user_by_email_role',
            {'email': email, 'role': role},
        )

    def create_user(self, email, password, role, check_user_validity: bool = True):
        return self.database_adapter.safe_execute(
            'create_user',
            {
                'email': email,
                'password': password,
                'role': role,
                'check_user_validity': check_user_validity,
            },
        )

    def find_by_id(self, user_id):
        return self.database_adapter.safe_execute(
            'find_user_by_id',
            {'user_id': user_id},
        )
