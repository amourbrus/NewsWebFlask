from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import create_app, db
from info import models
app = create_app("development")
manager = Manager(app)
Migrate(app, db)
manager.add_command("mysql", MigrateCommand)



if __name__ == '__main__':
    # print(app.url_map)
    manager.run()