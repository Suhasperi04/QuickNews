from flask import Flask, render_template, redirect, request, session
import json
import sys
sys.path.append("..")  # so it can access credentials.py from parent folder


from credentials import ADMIN_EMAIL, ADMIN_PASSWORD


import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATE_FILE = os.path.join(BASE_DIR, 'utils', 'state.json')


def set_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump({"status": state}, f)

def get_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("status", "UNKNOWN")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect("/dashboard")
        return " Invalid credentials"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")
    state = get_state()
    return render_template("index.html", status=state)

@app.route("/stop")
def stop():
    if not session.get("logged_in"):
        return redirect("/")
    set_state("PAUSED")
    return redirect("/dashboard")

@app.route("/start")
def start():
    if not session.get("logged_in"):
        return redirect("/")
    set_state("RUNNING")
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
