from flask import Blueprint


# Define the blueprint for authentication-related routes
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
    static_folder="static",
)

from . import routes 
