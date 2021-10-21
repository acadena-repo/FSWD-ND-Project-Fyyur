import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
user = os.environ.get('DBUSER')
pwsd = os.getenv('PASSWORD')
dtbs = os.getenv('DATABASE')

SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{user}:{pwsd}@localhost:5432/{dtbs}'

# Disable modifications tracking
SQLALCHEMY_TRACK_MODIFICATIONS = False