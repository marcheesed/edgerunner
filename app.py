from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from datetime import datetime
import random
import json
import os
from dotenv import load_dotenv
import json

app = Flask(__name__)
app.secret_key = "jason"  # required for sessions

load_dotenv()

TODO_FILE = "todos.json"
TAROT_FILE = "tarot.json"
FEELING_FILE = "feeling.json"
QUOTES_FILE = "quotes.json"
LAST_UPDATED_FILE = "last_updated.json"

# these are a fallback incase the json doesnt work
default_quotes = [
    "if you're seeing this then the quote generator has failed and marcy is an idiot"
]


with open("quotes.json", "r") as f:
    data = json.load(f)

if not isinstance(data, list):
    with open("quotes.json", "w") as f:
        json.dump(default_quotes, f, indent=4)


# ------------------ helpers ------------------
def load_quotes():
    if os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                # fallback to default if file is corrupted
                return default_quotes.copy()
    return default_quotes.copy()

def save_quotes(quotes):
    with open(QUOTES_FILE, "w") as f:
        json.dump(quotes, f, indent=4)

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

def load_last_updated():
    if os.path.exists(LAST_UPDATED_FILE):
        with open(LAST_UPDATED_FILE, "r") as f:
            return json.load(f)
    return {"date": None}

def save_last_updated(data):
    with open(LAST_UPDATED_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ routes ------------------

@app.route("/", methods=["GET", "POST"])
def index():
    todos = load_todos()
    tarot = load_tarot()
    feeling = load_feeling()
    quotes_list = load_quotes()
    
    # load last updated
    last_updated = {}
    if os.path.exists(LAST_UPDATED_FILE):
        last_updated = load_last_updated()

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "todo":
            task = request.form.get("task")
            password = request.form.get("password")
            if task and (session.get('password') or password):
                if password:
                    session['password'] = password
                todos.append({"task": task, "done": False})
                save_todos(todos)


        elif form_type == "tarot" and session.get('password'):
            card = request.form.get("card")
            if card:
                tarot = {"date": datetime.now().strftime("%Y-%m-%d"), "card": card}
                save_tarot(tarot)

        elif form_type == "feeling" and session.get('password'):
            character = request.form.get("character")
            if character:
                feeling = {"date": datetime.now().strftime("%Y-%m-%d"), "character": character}
                save_feeling(feeling)

        return redirect(url_for("index"))

    now = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")
    weather_api_key = "c9dc17589825d6c7f5d44c5c18827ac3"
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

    quote = random.choice(quotes_list)

    return render_template(
        "index.html",
        time=now,
        weather=weather,
        quote=quote,
        todos=todos,
        tarot=tarot,
        feeling=feeling,
        quotes=quotes_list,
        last_updated=last_updated,
    )

@app.route("/toggle/<int:index>", methods=["POST"])
def toggle(index):
    todos = load_todos()
    if not session.get('password'):
        return redirect(url_for("index"))
    if 0 <= index < len(todos):
        todos[index]["done"] = not todos[index]["done"]
        save_todos(todos)
    return redirect(url_for("index"))

@app.route("/set_last_updated", methods=["POST"])
def set_last_updated():
    if not session.get('password'):
        return redirect(url_for("index"))

    last_date = request.form.get("last_date")
    if last_date:
        last_updated = {"date": last_date}
        save_last_updated(last_updated)
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

@app.route("/api/status")
def api_status():
    now = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")
    weather_api_key = "c9dc17589825d6c7f5d44c5c18827ac3"
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
    return jsonify({"time": now, "weather": weather})

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

@app.route("/quotes", methods=["POST"], endpoint='quotes')
def edit_quotes():
    if not session.get('password'):
        return redirect(url_for("index"))

    action = request.form.get("action")
    quote_text = request.form.get("quote")
    index = request.form.get("index")

    quotes_list = load_quotes()

    if action == "add" and quote_text:
        quotes_list.append(quote_text)
    elif action == "edit" and quote_text and index is not None:
        idx = int(index)
        if 0 <= idx < len(quotes_list):
            quotes_list[idx] = quote_text
    elif action == "delete" and index is not None:
        idx = int(index)
        if 0 <= idx < len(quotes_list):
            quotes_list.pop(idx)

    save_quotes(quotes_list)
    return redirect(url_for("index"))

@app.route("/set_tarot", methods=["POST"])
def set_tarot():
    if not session.get('password'):
        return redirect(url_for("index"))
    card = request.form.get("card")
    if card:
        tarot = {"date": datetime.now().strftime("%Y-%m-%d"), "card": card}
        save_tarot(tarot)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
