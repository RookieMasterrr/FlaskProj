from flask import Flask
import os

def create_app():
    '''
    factory function.
    '''
    app = Flask(__name__)

    prefix = 'sqlite:///'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'user_data.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"]="iamasecret"

    app.config['WHOOSHEE_MIN_STRING_LEN']=1

    from .dbm import db,whooshee,mail
    mail.init_app(app)
    db.init_app(app)
    whooshee.init_app(app=app)
    whooshee.WHOOSHEE_MIN_STRING_LEN=1
    db.create_all(app=app)

    from . import videos_module
    app.register_blueprint(videos_module.bp,url_prefix='/api/v1/videos')

    from . import users_module
    app.register_blueprint(users_module.bp,url_prefix='/api/v1/users')

    from . import tweets_module
    app.register_blueprint(tweets_module.bp,url_prefix='/api/v1/tweets')

    from . import root_module
    app.register_blueprint(root_module.bp,url_prefix='/api/v1/roots')

    @app.route('/')
    def originpage():
        return app.root_path

    return app  