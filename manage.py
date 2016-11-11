
import os

from flask_script import Manager

from bunbunmaru import create_app, db


app = create_app(os.path.abspath('config/development.py'))
manager = Manager(app)


@manager.command
def init():
    pass


if __name__ == '__main__':
    manager.run()
