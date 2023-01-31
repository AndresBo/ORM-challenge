from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

## DB CONNECTION AREA
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:paco@localhost:5432/ripe_tomatoes_db" 

db = SQLAlchemy(app)
ma = Marshmallow(app)
# CLI COMMANDS AREA
@app.cli.command("create")
def create_db():
  db.create_all()
  print("Tables Created")


@app.cli.command("drop")
def drop_db(): 
    db.drop_all()
    print("Tables dropped")


@app.cli.command("seed")
def seed_db():
    movie1 = Movie(
      title = "Jurassic Park",
      genre = "Action",
      length = "120",
      year = 1994
    )
    db.session.add(movie1)

    movie2 = Movie(
      title = "Dune",
      genre = "Science Fiction",
      length = 180,
      year = 2020
    )
    db.session.add(movie2)

    actor1 = Actor(
      name = "Robin Williams",
      gender = "Male",
      country = "USA",
      dob = '1950-10-01',
    )
    db.session.add(actor1)

    actor2 = Actor(
      name = "Ethan Hawke",
      gender = "Male",
      country = "USA",
      dob = '1950-10-01',
    )
    db.session.add(actor2)

    actor3 = Actor(
      name = "Uma Thurman",
      gender = "Female",
      country = "USA",
      dob = '1950-10-01',
    )
    db.session.add(actor3)

    db.session.commit()


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
    year = db.Column(db.Integer())


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
class ActorSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "gender", "country", "dob")

actors_schema = ActorSchema(many=True)


class MovieSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "genre", "length", "year")

movies_schema = MovieSchema(many=True)

# ROUTING AREA

@app.route("/")
def hello():
  return "Welcome to Ripe Tomatoes API"

@app.route("/movies", methods = ["GET"])
def get_actors():
    movies_list = Movie.query.all()
    result = movies_schema.dump(movies_list)
    return jsonify(result)


@app.route("/actors", methods = ["GET"])
def get_cards():
    actors_list = Actor.query.all()
    result = actors_schema.dump(actors_list)
    return jsonify(result)
