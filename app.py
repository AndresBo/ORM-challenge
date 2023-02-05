from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow.validate import Length
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta


app = Flask(__name__)

## DB CONNECTION AREA ###################################################################################################################
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:paco@localhost:5432/ripe_tomatoes_db" 

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "Backend best end"

# CLI COMMANDS AREA #####################################################################################################################
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


    admin_user = User(
      email = "admin",
      password = bcrypt.generate_password_hash("password123").decode("utf-8"),
      admin = True
    )
    db.session.add(admin_user)

    db.session.commit()
    print("Tables seeded")


# MODELS AREA ###########################################################################################################################
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


class User(db.Model):
  __tablename__ = "USERS"

  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(), nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False)
  admin = db.Column(db.Boolean(), default=False)

# SCHEMAS AREA ##############################################################################################################################
class ActorSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "gender", "country", "dob")

actor_schema = ActorSchema()
actors_schema = ActorSchema(many=True)


class MovieSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "genre", "length", "year")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    password = ma.String(validate=Length(min=8))

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# ROUTING AREA ##########################################################################################################################

@app.route("/")
def hello():
  return "Welcome to Ripe Tomatoes API"


@app.route("/movies", methods = ["GET"])
def get_actors():
    movies_list = Movie.query.all()
    result = movies_schema.dump(movies_list)
    return jsonify(result)


@app.route("/movies", methods=["POST"])
@jwt_required()
def movie_create():
    movie_fields = movie_schema.load(request.json)

    new_movie = Movie()
    new_movie.title = movie_fields["title"]
    new_movie.genre = movie_fields["genre"]
    new_movie.length = movie_fields["length"]
    new_movie.year = movie_fields["year"]
    
    db.session.add(new_movie)
    db.session.commit()

    return jsonify(movie_schema.dump(new_movie))


@app.route("/movies/<int:id>", methods=["DELETE"])
@jwt_required()

def movie_delete(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return abort(401, description="Invalid user")

    movie = Movie.query.filter_by(id=id).first()

    if not Movie:
        return abort(400, description= "Movie does not exists")

    db.session.delete(movie)
    db.session.commit()

    return jsonify(movie_schema.dump(movie))
    


@app.route("/actors", methods = ["GET"])
def get_cards():
    actors_list = Actor.query.all()
    result = actors_schema.dump(actors_list)
    return jsonify(result)


@app.route("/actors", methods=["POST"])
# decorator to make sure the jwt is included in the request
@jwt_required()
def actor_create():
    actor_fields = actor_schema.load(request.json)

    new_actor = Actor()
    new_actor.name = actor_fields["name"]
    new_actor.gender = actor_fields["gender"]
    new_actor.country = actor_fields["country"]
    new_actor.dob = actor_fields["dob"]

    db.session.add(new_actor)
    db.session.commit()

    return jsonify(actor_schema.dump(new_actor))


@app.route("/actors/<int:id>", methods=["DELETE"])
@jwt_required()
# includes the id parameter
def actor_delete(id):
    # get the user id invoking get_jwt_identity
    user_id = get_jwt_identity()
    # find it in the db
    user = User.query.get(user_id)
    # make sure it is in the database
    if not user:
        return abort(401, description="Invalid user")

    # find the actor
    actor = Actor.query.filter_by(id=id).first()
    # return an error if the card does not exists
    if not Actor:
        return abort(400, description="Actor does not exists")
    # Delete the actor from the db and commit
    db.session.delete(actor)
    db.session.commit()
    # return the card in the response
    return jsonify(actor_schema.dump(actor))
   ########################################### working here! 


@app.route("/auth/signup", methods=["POST"])
def auth_signup():
    # get user data from the request by loading in user_schema converted to JSON.
    user_fields = user_schema.load(request.json)

    # find user
    user = User.query.filter_by(email=user_fields["email"]).first()
    
    if user:
        # return abort message to inform user of same_email error, ending the request
        return abort(400, description="Email already registered")

    # create user objet
    user = User()
    # add the email attribute
    user.email = user_fields["email"]
    # add the password attribute hashed by bcrypt
    user.password = bcrypt.generate_password_hash(user_fields["password"]).decode("utf-8")
    # add to db and commit changes
    db.session.add(user)
    db.session.commit()
    # create a variable that sets and expiry date
    expiry = timedelta(days=1)
    # create the access token
    access_token = create_access_token(identity=str(user.id), expiries_delta=expiry)
    # return the user email and the access token
    return jsonify({"user":user.email, "token":access_token})


@app.route("/auth/signin", methods=["POST"])
def auth_signin():
    # get user data from the request
    user_fields = user_schema.load(request.json)
    # find the user in the db by email
    user = User.query.filter_by(email=user_fields["email"]).first()
    # there is not a user with that email or the password is not correnct, send error:
    if not user or not bcrypt.check_password_hash(user.password, user_fields["password"]):
        return abort(401, description="Incorrect username or password")

    #create variable that sets an expiry date
    expiry = timedelta(days=1)
    #create access token
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)

    return jsonify({"user":user.email, "token":access_token})
