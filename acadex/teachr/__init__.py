from flask import Blueprint

teachr_bp = Blueprint(
  'teachr_bp',
  __name__,
  url_prefix='/teacher',
  static_folder='static',
  template_folder='templates'
)

from . import routes