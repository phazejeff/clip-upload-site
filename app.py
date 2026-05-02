import io

from flask import Flask, send_file
from flask import render_template, request, redirect, flash, url_for, send_from_directory
from PIL import Image
import os
import hashlib
from video import write_first_frame

app = Flask(__name__)
app.secret_key = os.urandom(24)
PASSWORD = os.environ["password"]
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".webm", ".m4v"}

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

        file.save(UPLOAD_DIR + hash + extension)
        file.close()
        f = open(UPLOAD_DIR + hash + ".txt", "w+")
        f.writelines([name, "\n", request.form.get("public")])
        f.close()
        write_first_frame(UPLOAD_DIR, hash, extension)
        
        return redirect(url_for("clip", filename = hash + extension))
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
    f = open(UPLOAD_DIR + hash + ".txt")
    title = f.readline()
    f.close()
    img = hash + ".jpg"
    return render_template("clip.html", title=title, filename=filename, img=img)

@app.route("/api/clips")
def clips_api():
    admin = False
    if request.args.get("password") == PASSWORD:
        admin = True
    all_clips = []
    for filename in os.listdir(UPLOAD_DIR):
        if not filename.endswith(".txt") and not filename.endswith(".jpg"):
            hash = filename.removesuffix("." + filename.split(".")[-1])
            with open(os.path.join(UPLOAD_DIR, hash + ".txt")) as f:
                title = f.readline().strip()
                public = f.readline().strip()
            if "true" in public or admin:
                all_clips.append({filename : {"title": title, "public": public}})
    return all_clips

@app.route("/photo/<filename>")
def photo(filename: str, quality: int = 30):
    if not filename.endswith(".jpg"):
        return "Invalid filetype", 400
    
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    img = Image.open(filepath)
    img_io = io.BytesIO()
    img.save(img_io, format="JPEG", quality=quality)  # 1–95, lower = smaller file
    img_io.seek(0)
    
    return send_file(img_io, mimetype="image/jpeg")

@app.route("/clips")
def clips_page():
    return render_template("clips.html")

@app.route("/api/clip/<filename>/edit", methods=["POST"])
def edit_clip(filename: str):
    if request.form.get("password") != PASSWORD:
        return "Unauthorized", 401
    extension = "." + filename.split(".")[-1]
    hash = filename.removesuffix(extension)
    f = open(UPLOAD_DIR + hash + ".txt", "w")
    f.writelines([request.form.get("title"), "\n", request.form.get("public")])
    f.close()
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