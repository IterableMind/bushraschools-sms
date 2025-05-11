# Handle application configuration
import os
from secrets import token_hex

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or token_hex(32)
  # Base directory of the app
  basedir = os.path.abspath(os.path.dirname(__file__))

  # Define the path to the instance folder and the SQLite database file
  instance_path = os.path.join(basedir, 'instance')  # instance folder
  if not os.path.exists(instance_path):
    os.makedirs(instance_path)  # Create the instance folder if it doesn't exist

  # Use the instance folder for the SQLite database file
  SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'app.db')}"
#   SQLALCHEMY_DATABASE_URI = 'postgresql://bushra_user:t6LIfL0F61gZMWHw2ZDJo3QN1JPTKNf3@dpg-d0fu4oq4d50c73f9lgig-a/bushra'
  SQLALCHEMY_TRACK_MODIFICATIONS = False