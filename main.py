from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation, dip_operation):
    print(f"Processing - Operation: {operation}, DIP Operation: {dip_operation}")  # Debugging

    img = cv2.imread(f"uploads/{filename}")
    newFilename = f"static/{filename}"

    # Handle format conversions
    if operation in ["cgray", "cwebp", "cjpeg", "cpng"]:
        if operation == "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif operation == "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            imgProcessed = img
        elif operation == "cjpeg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            imgProcessed = img
        elif operation == "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            imgProcessed = img

    # Handle DIP operations
    elif dip_operation in ["edge", "blur", "threshold", "hist_eq"]:
        if dip_operation == "edge":
            imgProcessed = cv2.Canny(img, 100, 200)
        elif dip_operation == "blur":
            imgProcessed = cv2.GaussianBlur(img, (7, 7), 0)
        elif dip_operation == "threshold":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, imgProcessed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        elif dip_operation == "hist_eq":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgProcessed = cv2.equalizeHist(gray)

    else:
        return None  # Return None if no valid operation

    cv2.imwrite(newFilename, imgProcessed)
    return newFilename


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation", "").strip()
        dip_operation = request.form.get("dip_operation", "").strip()
        
        print(f"Received operation: {operation}, DIP operation: {dip_operation}")  # Debugging

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new = processImage(filename, operation, dip_operation)
            if new:
                flash(f"Image processed successfully. Download it <a href='/{new}' target='_blank'>here</a>.")
            else:
                flash("Invalid operation selected.")  # Error message

            return render_template("index.html")

    return render_template("index.html")


app.run(debug=True)
