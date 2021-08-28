from flask import Blueprint,send_from_directory,current_app
import os

from werkzeug.utils import secure_filename
from .func import localURL




bp = Blueprint('root_module', __name__, url_prefix='/root')
projectPath=os.path.dirname(__file__)

@bp.route('/',methods=["GET"])
def error_test():
    filename="home/username/.bashrc"
    print(filename)
    print(secure_filename(filename))
    return "Its root page"

@bp.route('/download',methods=["GET"])
def downloal():
    return send_from_directory(projectPath,'user_data.db')