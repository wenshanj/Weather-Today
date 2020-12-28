#!/usr/bin/env python3

import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SECRET_KEY"] = "secret"
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False)

def getCityHelper(city):
    url= f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=dc16f1253d2f9642cf3c69b70a073368"
    r = requests.get(url).json()
    return r 


@app.route("/", methods=["GET"])
def indexGet():
    cities = City.query.all()
    weatherLst = []
    for city in cities:
        r = getCityHelper(city.name)
        stat = {
            "city" : city.name,
            "temperature" : r["main"]["temp"],
            "description" : r["weather"][0]["description"],
            "feelslike" : r["main"]["feels_like"],
            "icon" : r["weather"][0]["icon"]
        }
        weatherLst.insert(0, stat)
    return render_template("index.html", weatherLst=weatherLst)

@app.route("/", methods=["POST"])
def indexPost():
    errMsg = ""
    newCity = request.form.get("city")
    s = ""
    for char in newCity.split(" "):
        s += char.capitalize()
        s += " "
    if s != "":
        existingCity = City.query.filter_by(name=s).first()
        if not existingCity:
            data = getCityHelper(s)
            if data["cod"] == 200:
                newCityDB = City(name=s)
                db.session.add(newCityDB)
                db.session.commit()
            else:
                errMsg = f"{s} does not exist! Try again"
        else:
            errMsg = f"{s} added already!"
    if errMsg == "":
        flash(f"{s} added successfully!")
    else:
        flash(errMsg, "error")
    return redirect(url_for("indexGet"))


@app.route("/delete/<name>")
def deleteCity(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f"Successfully deleted {city.name}", "success")
    return redirect(url_for("indexGet"))

if __name__ == '__main__':
    app.run(debug=True)