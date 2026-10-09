from flask import Flask, render_template, request
import os

app = Flask(**name**)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt", "doc", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_resume():
if request.method == "POST":
if "resume" not in request.files:
return "No resume file selected", 400

```
    file = request.files["resume"]

    if file.filename == "":
        return "Please select a file", 400

    extension = file.filename.rsplit(".", 1)[-1].lower()

    if "." not in file.filename or extension not in ALLOWED_EXTENSIONS:
        return "Unsupported file type", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    return render_template("result.html", filename=file.filename)

return render_template("upload.html")
```

if **name** == "**main**":
app.run(host="0.0.0.0", port=5000)
