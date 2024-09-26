import datetime
import json

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)


def load_clubs():
    with open("clubs.json") as c:
        list_of_clubs = json.load(c)["clubs"]
        return list_of_clubs


def load_competitions():
    with open("competitions.json") as comps:
        list_of_competitions = json.load(comps)["competitions"]
        return list_of_competitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = load_competitions()
clubs = load_clubs()


@app.route("/")
def index():
    """Renders login form. if form_valid redirect to show_summary"""
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():
    club = [club for club in clubs if club["email"] == request.form["email"]]
    if not club:
        flash("No club found with this email")
        return render_template("index.html")
    else:
        session.clear()
        session["user_id"] = club[0]["email"]
        past_competitions = [
            comp
            for comp in competitions
            if datetime.datetime.fromisoformat(comp["date"]) < datetime.datetime.now()
        ]
        return render_template(
            "welcome.html",
            club=club[0],
            competitions=competitions,
            past_competitions=past_competitions,
        )


@app.route("/book/<competition>/<club>")
def book(competition, club):
    found_club = [c for c in clubs if c["name"] == club][0]
    found_competition = [c for c in competitions if c["name"] == competition][0]
    if found_club and found_competition:
        if (
            datetime.datetime.fromisoformat(found_competition["date"])
            < datetime.datetime.now()
        ):
            flash("You cannot book places for a past event.")
            return render_template("welcome.html", club=club, competitions=competitions)
        return render_template(
            "booking.html", club=found_club, competition=found_competition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    available_points = int(club["points"])
    points_required_per_place = 3
    places_required = int(request.form["places"])
    
    if places_required > 12:
        flash("You cannot book more than 12 places for each competition")
    elif places_required > int(competition["numberOfPlaces"]):
        flash("You can't buy more places than there are availables")
    elif available_points * points_required_per_place < int(competition["numberOfPlaces"]):
        flash("You don't have enough points to purchase this amount of places !")
    else:
        competition["numberOfPlaces"] = (
            int(competition["numberOfPlaces"]) - places_required
        )
        club["points"] = available_points - places_required * points_required_per_place
        flash("Great - booking complete!")

    return render_template("welcome.html", club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/fullDisplay")
def full_display():
    return render_template("full_display.html", clubs=clubs)
