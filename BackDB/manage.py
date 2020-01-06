from flask_script import Manager
from app import app
from flask_migrate import Migrate, MigrateCommand
from models import UserProfile, Host, DB, db


manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
