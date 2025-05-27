from cs50 import SQL
import calendar
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functools import wraps


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
TODAY = datetime.now()
LASTDAY = {}
EVENTS = ["Birthday", "Anniversary", "Football", "Miscellaneous"]

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///events.db")

@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    global LASTDAY
    month = TODAY.month
    year = TODAY.year
    date = TODAY.day
    cal = calendar.Calendar().monthdays2calendar(year, month)
    LASTDAY = {"dt": date, "mnth":month, "yr": year}

    birthdays = db.execute("SELECT * FROM events WHERE event = 'Birthday' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
    anniversaries = db.execute("SELECT * FROM events WHERE event = 'Anniversary' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
    matches = db.execute("SELECT * FROM events WHERE event = 'Football' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
    miscellaneousList = db.execute("SELECT * FROM events WHERE event = 'Miscellaneous' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)

    return render_template("index.html", calender = cal, date = date, month = MONTHS[month - 1], year = year, birthdays = birthdays, anniversaries = anniversaries, matches = matches, miscellaneousList = miscellaneousList)


@app.route("/changeCal", methods = ["GET", "POST"])
@login_required
def changeCal():
    global LASTDAY
    if request.method == "POST":
        input0 = request.form.get("cal")
        year = int(input0[0:4])
        month = int(input0[5:7])
        date = int(input0[8:10])
        LASTDAY = {"dt": date, "mnth":month, "yr": year}
        cal = calendar.Calendar().monthdays2calendar(year, month)
        birthdays = db.execute("SELECT * FROM events WHERE event = 'Birthday' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
        anniversaries = db.execute("SELECT * FROM events WHERE event = 'Anniversary' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
        matches = db.execute("SELECT * FROM events WHERE event = 'Football' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
        miscellaneousList = db.execute("SELECT * FROM events WHERE event = 'Miscellaneous' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], month)
        return render_template("index.html", calender = cal, date = date, month = MONTHS[month - 1], year = year, birthdays = birthdays, anniversaries = anniversaries, matches = matches, miscellaneousList = miscellaneousList)
    date = LASTDAY["dt"]
    month = LASTDAY["mnth"]
    year = LASTDAY["yr"]
    cal = calendar.Calendar().monthdays2calendar(year, month)
    birthdays = db.execute("SELECT * FROM events WHERE event = 'Birthday' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], TODAY.month)
    anniversaries = db.execute("SELECT * FROM events WHERE event = 'Anniversary' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], TODAY.month)
    matches = db.execute("SELECT * FROM events WHERE event = 'Football' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], TODAY.month)
    miscellaneousList = db.execute("SELECT * FROM events WHERE event = 'Miscellaneous' AND user_id = ? ORDER BY CASE WHEN month >= ? THEN 0 ELSE 1 END, month, date", session["user_id"], TODAY.month)
    return render_template("index.html", calender = cal, date = date, month = MONTHS[month - 1], year = year, text = "Event Added Succesfully!", birthdays = birthdays, anniversaries = anniversaries, matches = matches, miscellaneousList = miscellaneousList)
    

@app.route("/changeDate", methods = ["GET", "POST"])
@login_required
def changeDate():
     global LASTDAY
     if request.method == "POST":
        date = int(request.form.get("date"))
        monthstr = request.form.get("month")
        for i in range(len(MONTHS)):
            if MONTHS[i] == monthstr:
                month = i + 1
        year = int(request.form.get("year"))
        cal = calendar.Calendar().monthdays2calendar(year, month)
        LASTDAY = {"dt": date, "mnth":month, "yr": year}
        return render_template("index.html", calender = cal, date = date, month = MONTHS[month - 1], year = year)
     
@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html")     
     

@app.route("/addEvent", methods = ["GET","POST"])
@login_required
def addEvent():
    user = session["user_id"]
    event = request.form.get("eventType")
    date = int(request.form.get("date"))
    month = MONTHS.index(request.form.get("month")) + 1
    year = int(request.form.get("year"))
    description = request.form.get("dynamicInput")
    if event in ["Anniversary","Birthday"]:
        db.execute(
            "INSERT INTO events (user_id, event, date, month, description) VALUES (?,?,?,?,?)",user,event,date,month,description,
        )    
    else:
        db.execute(
            "INSERT INTO events (user_id, event, date, month,year, description) VALUES (?,?,?,?,?,?)",user,event,date,month,year,description,
        )  
    return redirect("/changeCal")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", text = "ENTER USERNAME", green = 0)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", text = "ENTER PASSWORD", green = 0)
        
        rows = db.execute("SELECT * from users where user = ?", request.form.get("username"))

        if not rows:
            return render_template("login.html", text = "INVALID USER", green = 0)

        if rows[0]["password"]  != request.form.get("password"):
            return render_template("login.html", text = "INVALID PASSWORD", green = 0)
        
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", text = "ENTER USERNAME")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", text = "ENTER PASSWORD")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", text = "PASSWORD DOESN'T MATCH")
        rows = db.execute("SELECT * from users where user = ?", request.form.get("username"))

        if not rows:
            db.execute(
                "INSERT INTO users (user, password) VALUES (?,?)",
                request.form.get("username"),
                request.form.get("password"),
            )
            return render_template("login.html", text = "SUCCESFULLY REGISTERED", green = 1)       
        else:
            return render_template("register.html", text = "USERNAME ALREADY TAKEN")

    return render_template("register.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/events", methods = ["GET", "POST"])
@login_required
def events():
    if request.method == "POST":
        db.execute("DELETE FROM events WHERE event_id = ?", request.form.get("remove"))
    data = []
    for event in EVENTS:
        if event == "Football":
            temp =  db.execute("SELECT * FROM events WHERE event = ? AND user_id = ? ORDER BY year, month, date", event, session["user_id"])
        else:
            temp =  db.execute("SELECT * FROM events WHERE event = ? AND user_id = ? ORDER BY month, date", event, session["user_id"])
        data.append(temp)
    return render_template("events.html", EVENTS = EVENTS, data = data, MONTHS = MONTHS)



if __name__ == '__main__':
    app.run(debug=True)