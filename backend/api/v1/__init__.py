from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

from . import auth
from . import users
from . import files
from . import notes
from . import tasks
from . import settings
from . import docs
