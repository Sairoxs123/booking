from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from cs50 import SQL
from datetime import datetime


app = Flask(__name__)


# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def number_in_range(ending, start, number):
    if number in range(start, ending):
        return False
    else:
        return True


starting_periods = [1, 2, 3, 4, 5, 6, 7, 8]
ending_periods = [2, 3, 4, 5, 6, 7, 8, 9]



db = SQL("mysql://root:YuFceU03fkHwBh2ScInC@containers-us-west-160.railway.app:6275/railway")

admin_password = "schoolpassword"

# Main route
@app.route("/")
def main():
    return render_template("index.html")


# DESKTOP WEBSITE ROUTES

@app.route("/desktop")
def desktop_main():
    return render_template("desktop/index.html")

# Booking page
@app.route("/desktop/booking")
def booking():
    return render_template("desktop/booking.html")

# Shows booked timings on chose date
@app.route("/desktop/check", methods = ["POST", "GET"])
def check():
    if request.method == "POST":
        date = request.form.get("date").lower().strip()
        results = db.execute("SELECT name, starting_period, ending_period, purpose FROM booking WHERE date = (?) ORDER BY starting_period", date)
        return render_template("desktop/available.html", info = results, date = date, start = starting_periods, end = ending_periods)

    return redirect("/desktop/booking")

# Books the auditorium
@app.route("/desktop/book", methods = ["POST", "GET"])
def book():
    if request.method == "POST":
        name = request.form.get("name").lower().strip()
        email = request.form.get("email").lower().strip()
        start = int(request.form.get("start").lower().strip())
        end = int(request.form.get("end").lower().strip())
        date = request.form.get("date").strip()
        if start not in starting_periods or end not in ending_periods:
            return render_template("failure.html", error = "period")
        purpose = request.form.get("purpose").lower().strip()

        if name == "" or email == "" or start == "" or end == "":
            return render_template("desktop/failure.html", error = "empty")

        if start > end:
            return render_template("desktop/failure.html", error = "greater")

        if start == end:
            return render_template("desktop/failure.html", error = "timings")

        if "@jsspsdubai.com" not in email:
            return render_template("desktop/failure.html", error = "email")

        now = datetime.now()

        current_time = now.strftime("%d/%m/%Y %H:%M:%S")

        results = db.execute("SELECT starting_period, ending_period FROM booking WHERE date = (?)", date)
        for i in results:
            if number_in_range(i["ending_period"], i["starting_period"], start) == False or number_in_range(i["ending_period"] + 1, i["starting_period"] + 1, end) == False:
                allresults = db.execute("SELECT * FROM booking WHERE date = (?) AND starting_period = (?)", date, start)
                return render_template("desktop/failure.html", error = "booked", results = allresults)

        db.execute("INSERT INTO booking (name, email, time_of_booking, date, starting_period, ending_period, purpose) VALUES (?, ?, ?, ?, ?, ?, ?)", name, email, current_time, date, start, end, purpose)
        db.execute("INSERT INTO booking_history (name, email, time_of_booking, date, starting_period, ending_period, purpose) VALUES (?, ?, ?, ?, ?, ?, ?)", name, email, current_time, date, start, end, purpose)
        return render_template("desktop/success.html", info = "reserved")

    return redirect("/desktop/booking")

# Returns delete page
@app.route("/desktop/delete-booking", methods = ["POST", "GET"])
def delbook():
    if request.method == "POST":
        name = request.form.get("name").lower().strip()
        email = request.form.get("email").lower().strip()
        date = request.form.get("date").lower().strip()
        start = request.form.get("start").lower().strip()
        end = request.form.get("end").lower().strip()

        if name == "" or email == "" or date == "" or start == "" or end == "":
            return render_template("desktop/failure.html", error = "empty")

        results = db.execute("SELECT * FROM booking WHERE name = (?) AND email = (?) AND date = (?) AND starting_period = (?) AND ending_period = (?)", name, email, date, start, end)

        if results:
            db.execute("DELETE FROM booking WHERE name = (?) AND email = (?) AND date = (?) AND starting_period = (?) AND ending_period = (?)", name, email, date, start, end)
        else:
            return render_template("desktop/failure.html", error = "booking no exist")

        return render_template("desktop/success.html", info = "deleted")

    return render_template("desktop/delete.html", start = starting_periods, end = ending_periods)


# Admin login
@app.route("/desktop/admin-login", methods = ["POST", "GET"])
def admin_login():
    if request.method == "POST":
        login = request.form.get("login")
        if not login:
            return render_template("desktop/admin-login.html", error = "empty")

        if login != admin_password:
            return render_template("desktop/admin-login.html", error = "wrong")

        session["logged-in"] = "True"

        return redirect("/desktop/admin-access")

    return render_template("desktop/admin-login.html")

# Allows admin to view booked timings
@app.route("/desktop/admin-access")
def access():
    if session.get("logged-in"):
        if session["logged-in"] == "True":
            results = db.execute("SELECT * FROM booking ORDER BY date")
            return render_template("desktop/admin.html", results = results)

    return redirect("/admin")

# Logout route
@app.route("/desktop/logout")
def logout():
    session["logged-in"] = None
    return redirect("/desktop/admin-login")

# Allows admin to delete booked timings
@app.route("/desktop/admin-delete", methods = ["POST"])
def admin_delete():
    name = request.form.get("name").lower().strip()
    email = request.form.get("email").lower().strip()
    date = request.form.get("date").lower().strip()
    start = request.form.get("start").lower().strip()
    end = request.form.get("end").lower().strip()

    if name == "" or email == "" or date == "" or start == "" or end == "":
        return render_template("desktop/failure.html", error = "empty")

    db.execute("DELETE FROM booking WHERE name = (?) AND email = (?) AND date = (?) AND starting_period = (?) AND ending_period = (?)", name, email, date, start, end)
    return redirect("/desktop/admin-access")


# MOBILE WEBSITE ROUTES

@app.route("/mobile")
def mobile_main():
    return render_template("mobile/index.html")

# Booking page
@app.route("/mobile/booking")
def mobile_booking():
    return render_template("mobile/booking.html")

# Shows booked timings on chose date
@app.route("/mobile/check", methods = ["POST", "GET"])
def mobile_check():
    if request.method == "POST":
        date = request.form.get("date").lower().strip()
        results = db.execute("SELECT name, starting_period, ending_period, purpose FROM booking WHERE date = (?) ORDER BY starting_period", date)
        return render_template("mobile/available.html", info = results, date = date, start = starting_periods, end = ending_periods)

    return redirect("/mobile/booking")

# Books the auditorium
@app.route("/mobile/book", methods = ["POST", "GET"])
def mobile_book():
    if request.method == "POST":
        name = request.form.get("name").lower().strip()
        email = request.form.get("email").lower().strip()
        start = int(request.form.get("start").lower().strip())
        end = int(request.form.get("end").lower().strip())
        date = request.form.get("name").strip()
        if start not in starting_periods or end not in ending_periods:
            return render_template("failure.html", error = "period")
        purpose = request.form.get("purpose").lower().strip()

        if name == "" or email == "" or start == "" or end == "":
            return render_template("mobile/failure.html", error = "empty")

        if start > end:
            return render_template("mobile/failure.html", error = "greater")

        if start == end:
            return render_template("mobile/failure.html", error = "timings")

        if "@jsspsdubai.com" not in email:
            return render_template("mobile/failure.html", error = "email")

        now = datetime.now()

        current_time = now.strftime("%d/%m/%Y %H:%M:%S")

        results = db.execute("SELECT starting_period, ending_period FROM booking WHERE date = (?)", date)
        for i in results:
            if number_in_range(i["ending_period"], i["starting_period"], start) == False or number_in_range(i["ending_period"] + 1, i["starting_period"] + 1, end) == False:
                allresults = db.execute("SELECT * FROM booking WHERE date = (?) AND starting_period = (?)", date, start)
                return render_template("mobile/failure.html", error = "booked", results = allresults)

        db.execute("INSERT INTO booking (name, email, time_of_booking, date, starting_period, ending_period, purpose) VALUES (?, ?, ?, ?, ?, ?, ?)", name, email, current_time, date, start, end, purpose)
        db.execute("INSERT INTO booking_history (name, email, time_of_booking, date, starting_period, ending_period, purpose) VALUES (?, ?, ?, ?, ?, ?, ?)", name, email, current_time, date, start, end, purpose)

        return render_template("mobile/success.html", info = "reserved")

    return redirect("/mobile/booking")

# Returns delete page
@app.route("/mobile/delete-booking", methods = ["POST", "GET"])
def mobile_delbook():
    if request.method == "POST":
        name = request.form.get("name").lower().strip()
        email = request.form.get("email").lower().strip()
        date = request.form.get("date").lower().strip()
        start = request.form.get("start").lower().strip()
        end = request.form.get("end").lower().strip()

        if name == "" or email == "" or date == "" or start == "" or end == "":
            return render_template("mobile/failure.html", error = "empty")

        results = db.execute("SELECT * FROM booking WHERE name = (?) AND email = (?) AND date = (?) AND starting_period = (?) AND ending_period = (?)", name, email, date, start, end)

        if results:
            db.execute("DELETE FROM booking WHERE name = (?) AND email = (?) AND date = (?) AND starting_period = (?) AND ending_period = (?)", name, email, date, start, end)
        else:
            return render_template("mobile/failure.html", error = "booking no exist")

        return render_template("desktop/success.html", info = "deleted")

    return render_template("desktop/delete.html", start = starting_periods, end = ending_periods)


# ERROR HANDLERS
@app.errorhandler(404)
def error404(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def error500(e):
    return render_template("500.html"), 500
