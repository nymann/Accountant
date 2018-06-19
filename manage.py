from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from project import app
from project.models import db


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project/database.db'

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
