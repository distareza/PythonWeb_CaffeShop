import random

import requests
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField, SubmitField, DecimalField, FloatField, BooleanField
from wtforms.validators import DataRequired, URL, Length
import myconfiguration

app = Flask(__name__)

app.config['SECRET_KEY'] = myconfiguration.secret_key

#Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # Helper function
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class CafeForm(FlaskForm):
    # https://www.digitalocean.com/community/tutorials/how-to-use-and-validate-web-forms-with-flask-wtf
    cafe_name = StringField('Cafe name', validators=[DataRequired(), Length(max=250)])
    location = SelectField('Cafe Location', choices=[
                    "London Bridge", "Peckham", "Bermodsey", "Hackney", "Shoreditch", "Clerkenwell", "Whitechapel",
                    "Bankside", "Barbican", "Shouth Kensington", "Borough"]
                    , validators=[DataRequired(), Length(max=250)])
    map_url = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL(), Length(max=500)])
    img_url = StringField("Cafe Image (URL)", validators=[DataRequired(), URL(), Length(max=500)])
    coffee_price = StringField("Cafe price", validators=[DataRequired()])
    has_toilet = BooleanField("Has toilet")
    has_wifi = BooleanField("Has wifi")
    has_socket = BooleanField("Has power socket")
    can_take_calls = BooleanField("Can take calls")
    seat_available = SelectField('Seat Available', choices=[ "0 - 10", "10-20", "20-30", "40-50", "50+"], validators=[DataRequired()])


class User(UserMixin):

    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

USER = { 0: User(0, "admin", "administrator", "test123") }

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return USER.get(user_id)
    except:
        return None

@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        for user in USER:
            if email == USER.get(user).email and password == USER.get(user).password:
                login_user(USER.get(user))
                return redirect(url_for("home"))

        return redirect(url_for("login"))
    return render_template("login_page.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html")

@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def readRecord():
    return jsonify( [ item.to_dict() for item in db.session.query(Cafe).all() ] )

@app.route("/get/<int:cafe_id>")
def getRecord(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        return jsonify(cafe), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

@app.route("/show/<int:cafe_id>")
def showRecord(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:

        form = CafeForm()
        form.cafe_name.data = cafe.name
        form.location.data = cafe.location
        form.map_url.data = cafe.map_url
        form.img_url.data = cafe.img_url
        form.coffee_price.data = cafe.coffee_price
        form.has_toilet.data = cafe.has_toilet
        form.has_wifi.data = cafe.has_wifi
        form.has_socket.data = cafe.has_sockets
        form.can_take_calls.data = cafe.can_take_calls
        form.seat_available.data = cafe.seats

        return render_template("cafe_detail.html", form=form, cafe_id=cafe_id)
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/add", methods=['POST', 'GET'])
@login_required
def addRecord():
    try:
        form = CafeForm()
        if form.validate_on_submit():
            new_cafe = Cafe(
                name=form.cafe_name.data,
                map_url=form.map_url.data,
                img_url=form.img_url.data,
                location=form.location.data,
                has_sockets=bool(form.has_socket.data),
                has_toilet=bool(form.has_toilet.data),
                has_wifi=bool(form.has_wifi.data),
                can_take_calls=bool(form.can_take_calls.data),
                seats=form.seat_available.data,
                coffee_price=form.coffee_price.data,
            )
            db.session.add(new_cafe)
            db.session.commit()
            return render_template("index.html")
    except Exception as e:
        flash(e.args[0])

    return render_template("add_cafe.html", form=form)

@app.route("/update", methods=["POST"])
@login_required
def update():
    try:
        cafe_id = request.form["id"]
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            form = CafeForm()
            if form.validate_on_submit():
                cafe.name = form.cafe_name.data
                cafe.map_url = form.map_url.data
                cafe.img_url = form.img_url.data
                cafe.location = form.location.data
                cafe.has_sockets = bool(form.has_socket.data)
                cafe.has_toilet = bool(form.has_toilet.data)
                cafe.has_wifi = bool(form.has_wifi.data)
                cafe.can_take_calls = bool(form.can_take_calls.data)
                cafe.seats = form.seat_available.data
                cafe.coffee_price = form.coffee_price.data

                db.session.commit()

                #return redirect(url_for(f"/show/{cafe_id}"))
                return render_template("index.html")
            else:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    except Exception as e:
        return render_template("cafe_detail.html", form=form, cafe_id=cafe_id)

@app.route("/remove", methods=["POST"])
@login_required
def remove():
    cafe_id = request.form.get("id")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return render_template("index.html")
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)