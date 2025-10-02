from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import requests
from datetime import datetime
import random
import json
import os
from dotenv import load_dotenv
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz

london_tz = pytz.timezone("Europe/London")
now = datetime.now(london_tz).strftime("%A, %B %d, %Y %H:%M:%S")


app = Flask(__name__)
app.secret_key = "jason"  # required for sessions
APP_PASSWORD="jason"


load_dotenv()

TODO_FILE = "todos.json"
TAROT_FILE = "tarot.json"
FEELING_FILE = "feeling.json"
QUOTES_FILE = "quotes.json"
LAST_UPDATED_FILE = "last_updated.json"
SECTIONS_FILE = "sections.json"
UPLOAD_FOLDER = "submissions"
ADMIN_MEME_FILE = "admin_meme.json"


# these are a fallback incase the json doesnt work
default_quotes = [
    "if you're seeing this then the quote generator has failed and marcy is an idiot"
]

# default fallback in case file doesn't exist or is corrupted
default_sections = {
    "fandoms": "",
    "enjoy": "",
    "avoid": "",
    "characters": ""
}

# another default u know the deal by now
default_admin_meme = {
    "url": "https://file.garden/aBi0tvXzESnPXzr_/tumblr_d09e7e19f7f26dd0f80c0c2ba7b511dd_50474f34_400.webp",
    "caption": "marcy when it has to do any form of database work (fuck you sql)!!!!!!!"
}


with open("quotes.json", "r") as f:
    data = json.load(f)

if not isinstance(data, list):
    with open("quotes.json", "w") as f:
        json.dump(default_quotes, f, indent=4)
# Where submissions are stored (make sure this folder exists)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ helpers ------------------

def load_sections():
    if os.path.exists(SECTIONS_FILE):
        with open(SECTIONS_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    return default_sections.copy()

def save_sections(sections):
    with open(SECTIONS_FILE, "w") as f:
        json.dump(sections, f, indent=4)


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
    return []  # start with an empty list

def save_tarot(tarot_list):
    with open(TAROT_FILE, "w") as f:
        json.dump(tarot_list, f, indent=4)


def load_last_updated():
    if os.path.exists(LAST_UPDATED_FILE):
        with open(LAST_UPDATED_FILE, "r") as f:
            return json.load(f)
    return {"date": None}

def save_last_updated(data):
    with open(LAST_UPDATED_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_admin_meme():
    if os.path.exists(ADMIN_MEME_FILE):
        with open(ADMIN_MEME_FILE, "r") as f:
            return json.load(f)
    return default_admin_meme.copy()

def save_admin_meme(meme):
    with open(ADMIN_MEME_FILE, "w") as f:
        json.dump(meme, f, indent=4)

sections = load_sections()

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
                tarot_list = load_tarot()
                tarot_list.append({"date": datetime.now().strftime("%Y-%m-%d"), "card": card})
                save_tarot(tarot_list)


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
    tarot_history = load_tarot()
    latest_tarot = tarot_history[-1] if tarot_history else None

    return render_template(
        "index.html",
        tarot_history=tarot_history,
        tarot=latest_tarot,
        time=now,
        weather=weather,
        quote=quote,
        todos=todos,
        feeling=feeling,
        quotes=quotes_list,
        last_updated=last_updated,
        sections=sections
    )
@app.route("/art")
def art():
    return render_template("art.html")  # <-- make an art.html template

@app.route("/links")
def links():
    return render_template("links.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



@app.route("/set_sections", methods=["POST"])
def set_sections():
    if not session.get('password'):
        return redirect(url_for("index"))

    sections = load_sections()

    # get form data
    fandoms = request.form.get("fandoms")
    enjoy = request.form.get("enjoy")
    avoid = request.form.get("avoid")
    characters = request.form.get("characters")

    # update if provided
    if fandoms is not None:
        sections["fandoms"] = fandoms
    if enjoy is not None:
        sections["enjoy"] = enjoy
    if avoid is not None:
        sections["avoid"] = avoid
    if characters is not None:
        sections["characters"] = characters

    save_sections(sections)
    return redirect(url_for("index"))

@app.route("/extras")
def extras():
    from app import load_sections
    sections = load_sections()
    return render_template("extras.html", message="funky extras page", sections=sections)

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
    if pw and pw == APP_PASSWORD:
        session['password'] = pw
    # redirect back to the page the user submitted the form from
    return redirect(request.referrer or url_for("index"))


@app.route("/logout")
def logout():
    session.pop('password', None)
    return redirect(url_for("index"))

@app.route("/set_feeling", methods=["POST"])
def set_feeling():
    if not session.get('password'):
        return jsonify({"success": False, "error": "Not logged in"}), 403

    character = request.form.get("character")
    if character:
        feeling = {"date": datetime.now().strftime("%Y-%m-%d"), "character": character}
        save_feeling(feeling)
        return jsonify({"success": True, "character": character, "date": feeling["date"]})
    
    return jsonify({"success": False, "error": "No character provided"}), 400


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


@app.route("/set_admin_meme", methods=["POST"])
def set_admin_meme():
    if not session.get("password"):
        return redirect(url_for("index"))

    url = request.form.get("url")
    caption = request.form.get("caption")

    meme = load_admin_meme()
    if url:
        meme["url"] = url
    if caption:
        meme["caption"] = caption

    save_admin_meme(meme)
    return redirect(url_for("admin"))


@app.route("/set_tarot", methods=["POST"])
def set_tarot():
    if not session.get('password'):
        return jsonify({"success": False, "error": "Not logged in"}), 403

    card = request.form.get("card")
    if card:
        tarot_list = load_tarot()
        tarot_list.append({"date": datetime.now().strftime("%Y-%m-%d"), "card": card})
        save_tarot(tarot_list)
        return jsonify({"success": True, "card": card})
    
    return jsonify({"success": False, "error": "No card provided"}), 400


@app.route("/submit_pixelart", methods=["POST"])
def submit_pixelart():
    if "pixelart" not in request.files:
        return "No file uploaded", 400

    file = request.files["pixelart"]
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return "OK", 200

@app.route("/admin", endpoint="admin")
def admin():
    # Require password login
    if not session.get("password"):
        return redirect(url_for("index"))

    # --- pixel art submissions ---
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]

    # --- load data for dashboard ---
    sections = load_sections()
    todos = load_todos()
    quotes = load_quotes()
    feeling = load_feeling()
    tarot_history = load_tarot()
    latest_tarot = tarot_history[-1] if tarot_history else None
    last_updated = load_last_updated()
    meme = load_admin_meme()


    return render_template(
        "admin.html",
        files=files,
        sections=sections,
        todos=todos,
        quotes=quotes,
        feeling=feeling,
        tarot=latest_tarot,
        tarot_history=tarot_history,
        last_updated=last_updated,
        meme=meme,
    )

@app.route("/submissions/<filename>")
def get_submission(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)



if __name__ == "__main__":
    app.run(debug=True)
