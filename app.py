from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

## DB CONNECTION AREA
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:paco@localhost:5432/ripe_tomatoes_db" 

db = SQLAlchemy(app)
# CLI COMMANDS AREA

# MODELS AREA
class Movie(db.Model):
    #define the table name for the db
    __tablename__ = "MOVIES"
    #set the primary key 
    id = db.Column(db.Integer,primary_key = True)
    #set rest of attributes
    title = db.Column(db.String())
    genre = db.Column(db.String())
    length = db.Column(db.Integer())
    year = db.Column(db.Date())


class Actor(db.Model):
  #define the table name for the db
  __tablename__ = "ACTORS"
  #set the primary key
  id = db.Column(db.Integer,primary_key = True)
  #set rest of attributes
  name = db.Column(db.String())
  gender = db.Column(db.String())
  country = db.Column(db.String())
  dob = db.Column(db.Date())

# SCHEMAS AREA

# ROUTING AREA

@app.route("/")
def hello():
  return "Welcome to Ripe Tomatoes API"
