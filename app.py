from flask import Flask, send_file
from flask import render_template, request, redirect, flash, url_for, send_from_directory
from PIL import Image
import os
import hashlib
from video import process_video, write_first_frame
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
PASSWORD = os.environ["password"]
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".webm", ".m4v"}

if not os.path.exists(os.path.join(UPLOAD_DIR, "cache")):
    os.makedirs(os.path.join(UPLOAD_DIR, "cache"))

clips_cache: dict[str, dict] = {}  # { filename: { title, public } }

def load_cache():
    """Populate clips_cache from disk on startup."""
    for filename in os.listdir(UPLOAD_DIR):
        if filename in ("cache",) or filename.endswith((".txt", ".jpg")):
            continue
        hash = filename.removesuffix("." + filename.split(".")[-1])
        txt_path = os.path.join(UPLOAD_DIR, hash + ".txt")
        if os.path.exists(txt_path):
            with open(txt_path) as f:
                title = f.readline().strip()
                public = f.readline().strip()
            clips_cache[filename] = {"title": title, "public": public}

load_cache()

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if request.form.get("password") == PASSWORD:
        file = request.files["file"]
        hash = hashlib.md5(file.stream.read()).hexdigest()
        file.stream.seek(0)
        extension = "." + file.filename.split(".")[-1]
        name = file.filename.removesuffix(extension)
        if extension not in ALLOWED_EXTENSIONS:
            flash("Invalid filetype.")
            return redirect("/")

        file.save(os.path.join(UPLOAD_DIR, hash + extension))
        file.close()
        process_video(os.path.join(UPLOAD_DIR, hash + extension))
        f = open(os.path.join(UPLOAD_DIR, hash + ".txt"), "w+")
        f.writelines([name, "\n", request.form.get("public")])
        f.close()
        write_first_frame(UPLOAD_DIR, hash, extension)

        # Update cache
        filename = hash + extension
        clips_cache[filename] = {"title": name, "public": request.form.get("public")}

        return redirect(url_for("clip", filename=filename))
    else:
        flash("Incorrect Password")
        return redirect("/")

@app.route("/file/<filename>")
def file(filename: str):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/clip/<filename>")
def clip(filename: str):
    extension = "." + filename.split(".")[-1]
    hash = filename.removesuffix(extension)
    if filename not in clips_cache:
        txt_path = os.path.join(UPLOAD_DIR, hash + ".txt")
        if os.path.exists(txt_path):
            with open(txt_path) as f:
                title = f.readline().strip()
                public = f.readline().strip()
            clips_cache[filename] = {"title": title, "public": public}
        else:
            title = ""
    else:
        title = clips_cache[filename].get("title") or ""
    img = hash + ".jpg"
    return render_template("clip.html", title=title, filename=filename, img=img)

@app.route("/api/clips")
def clips_api():
    admin = request.args.get("password") == PASSWORD
    return [
        {filename: info}
        for filename, info in clips_cache.items()
        if "true" in info["public"] or admin
    ]

@app.route("/photo/<filename>")
def photo(filename: str, quality: int = 30):
    cache_path = os.path.join(UPLOAD_DIR, "cache", "thumb_" + filename)
    if os.path.exists(cache_path):
        return send_file(cache_path, mimetype="image/jpeg")
    
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        img = Image.open(filepath)
        img.save(cache_path, format="JPEG", quality=quality)
    except Exception:
        return send_file("static/finger smile resized.png", mimetype="image/png")
    
    return send_file(cache_path, mimetype="image/jpeg")

@app.route("/clips")
def clips_page():
    return render_template("clips.html")

@app.route("/api/clip/<filename>/edit", methods=["POST"])
def edit_clip(filename: str):
    if request.form.get("password") != PASSWORD:
        return "Unauthorized", 401
    extension = "." + filename.split(".")[-1]
    hash = filename.removesuffix(extension)
    title = request.form.get("title")
    public = request.form.get("public")
    with open(os.path.join(UPLOAD_DIR, hash + ".txt"), "w") as f:
        f.writelines([title, "\n", public])

    clips_cache[filename] = {"title": title, "public": public}

    return "Success", 200

@app.route("/clips/admin")
def admin_clips():
    return render_template("adminclips.html")

@app.route("/checkpassword", methods=["POST"])
def check_password():
    if request.form.get("password") == PASSWORD:
        return "Authorized", 200
    else:
        return "Unauthorized", 401

if __name__ == "__main__":
    app.run(debug=True)