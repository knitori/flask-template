
import os

from flask_script import Manager
from watchdog.observers import Observer

from bunbunmaru import create_app, db, scss

app = create_app(os.path.abspath('config/development.py'))
manager = Manager(app)


@manager.command
def init():
    pass


if __name__ == '__main__':
    scss_path = os.path.abspath('bunbunmaru/assets/scss/')
    target_path = os.path.abspath('bunbunmaru/assets/static/css/')

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        observer = Observer()
        observer.schedule(
            scss.ScssHandler('sassc', scss_path, target_path, 'styles'),
            scss_path,
            recursive=True
        )
        observer.start()

    try:
        manager.run()
    finally:
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            observer.stop()
