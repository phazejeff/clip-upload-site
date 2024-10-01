from flask import Flask
from flask import render_template, request, redirect, flash, url_for, send_from_directory
import os
import hashlib
from video import write_first_frame

app = Flask(__name__)
app.secret_key = os.urandom(24)
PASSWORD = os.environ["password"]
UPLOAD_DIR = "./uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".webm", ".m4v"}

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if request.form['password'] == PASSWORD:
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
        f.write(name)
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
    title = f.read()
    f.close()
    img = hash + ".jpg"
    return render_template("clip.html", title=title, filename=filename, img=img)

if __name__ == "__main__":
    app.run(debug=True)