from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from datetime import datetime
import random
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "jason"  # required for sessions

load_dotenv()


TODO_FILE = "todos.json"
TAROT_FILE = "tarot.json"
FEELING_FILE = "feeling.json"

quotes = [
    "TAKE A CHAAAAAAAAANCE WITH CHANCE BABY",
    # vocaloid
    "do you know fullness if you have never starved?",
    "all the words i left unsaid that day stained the sidewalk drop by drop with grey",
    "didn't you see the news today?",
    "if everybody accepts one day that they'll die they'd see the joy in life, and thats the reason we're alive!!!!!",
    # jade harley quotes
    "i guess it was just one more way everything got messed up for them.",
    "i would like to think that even if i was sad and scared, if i was put in a position where everyone depended on me, i could put all those feelings aside and do whats right!",
    "there's still something worth fighting for!!!!",
    # yonkagor quotes
    "we're fragile creatures made of love, we could act impulse when our lives get tough!",
    "now that i've things i hold dear, my fear of death has reappeared!",
    "yonkagor quote here",
]

# ------------------ helpers ------------------

def load_feeling():
    if os.path.exists(FEELING_FILE):
        with open(FEELING_FILE, "r") as f:
            return json.load(f)
    return {"date": None, "character": None}

def save_feeling(feeling):
    with open(FEELING_FILE, "w") as f:
        json.dump(feeling, f, indent=4)

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=4)

def load_tarot():
    if os.path.exists(TAROT_FILE):
        with open(TAROT_FILE, "r") as f:
            return json.load(f)
    return {"date": None, "card": None}

def save_tarot(tarot):
    with open(TAROT_FILE, "w") as f:
        json.dump(tarot, f, indent=4)

# ------------------ routes ------------------

@app.route("/", methods=["GET", "POST"])
def index():
    todos = load_todos()
    tarot = load_tarot()
    feeling = load_feeling()

    if request.method == "POST":
        form_type = request.form.get("form_type")  # identify which form submitted

        # ---------------- add to-do ----------------
        if form_type == "todo":
            task = request.form.get("task")
            password = request.form.get("password")

            if task and (session.get('password') or password):
                if password:
                    session['password'] = password
                todos.append({"task": task, "done": False})
                save_todos(todos)

        # ---------------- tarot ----------------
        elif form_type == "tarot":
            if session.get('password'):
                card = request.form.get("card")
                if card:
                    tarot = {"date": datetime.now().strftime("%Y-%m-%d"), "card": card}
                    save_tarot(tarot)

        # ---------------- feeling ----------------
        elif form_type == "feeling":
            if session.get('password'):
                character = request.form.get("character")
                if character:
                    feeling = {"date": datetime.now().strftime("%Y-%m-%d"), "character": character}
                    save_feeling(feeling)

        return redirect(url_for("index"))

    # get request handling
    now = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")

    # weather logic
    weather_api_key = os.getenv("WEATHER_API_KEY")
    city = "London"
    weather = "Weather unavailable"
    try:
        weather_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        ).json()
        if "main" in weather_data and "weather" in weather_data:
            weather = f"{weather_data['main']['temp']}°C, {weather_data['weather'][0]['description']}"
    except:
        pass

    quote = random.choice(quotes)

    return render_template("index.html", time=now, weather=weather, quote=quote, todos=todos, tarot=tarot, feeling=feeling)


@app.route("/toggle/<int:index>", methods=["POST"])
def toggle(index):
    todos = load_todos()
    if not session.get('password'):
        return redirect(url_for("index"))
    if 0 <= index < len(todos):
        todos[index]["done"] = not todos[index]["done"]
        save_todos(todos)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    todos = load_todos()
    if not session.get('password'):
        return redirect(url_for("index"))
    if 0 <= index < len(todos):
        todos.pop(index)
        save_todos(todos)
    return redirect(url_for("index"))

@app.route("/set_password", methods=["POST"])
def set_password():
    pw = request.form.get("password")
    if pw:
        session['password'] = pw
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop('password', None)
    return redirect(url_for("index"))

@app.route("/set_feeling", methods=["POST"])
def set_feeling():
    if not session.get('password'):
        return redirect(url_for("index"))
    character = request.form.get("character")
    if character:
        feeling = {"date": datetime.now().strftime("%Y-%m-%d"), "character": character}
        save_feeling(feeling)
    return redirect(url_for("index"))


# ------------------ tarot route ------------------

@app.route("/set_tarot", methods=["POST"])
def set_tarot():
    if not session.get('password'):
        return redirect(url_for("index"))

    card = request.form.get("card")
    if card:
        tarot = {"date": datetime.now().strftime("%Y-%m-%d"), "card": card}
        save_tarot(tarot)
    return redirect(url_for("index"))

# ------------------ main ------------------

if __name__ == "__main__":
    app.run(debug=True)
