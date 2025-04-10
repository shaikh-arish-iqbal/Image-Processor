from flask import Flask, render_template, request, flash, redirect
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

def processImage(filename, operation, dip_operation, advanced_operation):
    print(f"Processing - Operation: {operation}, DIP Operation: {dip_operation}, Advanced: {advanced_operation}")

    img = cv2.imread(f"uploads/{filename}")
    newFilename = f"static/{filename}"

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
        cv2.imwrite(newFilename, imgProcessed)
        return newFilename

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
        elif dip_operation == "compress":
            ext = filename.rsplit('.', 1)[1].lower()
            newFilename = f"static/{filename.split('.')[0]}_compressed.{ext}"
            if ext in ['jpg', 'jpeg']:
                cv2.imwrite(newFilename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                return newFilename
            elif ext == 'webp':
                cv2.imwrite(newFilename, img, [int(cv2.IMWRITE_WEBP_QUALITY), 50])
                return newFilename
            else:
                imgProcessed = img  # fallback for unsupported formats
                cv2.imwrite(newFilename, imgProcessed)
                return newFilename
        cv2.imwrite(newFilename, imgProcessed)
        return newFilename

    elif advanced_operation in ["rotate_left", "rotate_right", "flip_horizontal", "flip_vertical", "center_crop", "compress"]:
        if advanced_operation == "rotate_left":
            imgProcessed = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif advanced_operation == "rotate_right":
            imgProcessed = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif advanced_operation == "flip_horizontal":
            imgProcessed = cv2.flip(img, 1)
        elif advanced_operation == "flip_vertical":
            imgProcessed = cv2.flip(img, 0)
        elif advanced_operation == "center_crop":
            h, w = img.shape[:2]
            min_dim = min(h, w)
            start_x = w//2 - min_dim//2
            start_y = h//2 - min_dim//2
            imgProcessed = img[start_y:start_y+min_dim, start_x:start_x+min_dim]

        cv2.imwrite(newFilename, imgProcessed)
        return newFilename

    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation", "").strip()
        dip_operation = request.form.get("dip_operation", "").strip()
        advanced_operation = request.form.get("advanced_operation", "").strip()

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
            new = processImage(filename, operation, dip_operation, advanced_operation)
            if new:
                flash(f"Image processed successfully. Download it <a href='/{new}' target='_blank'>here</a>.")
            else:
                flash("Invalid operation selected.")

            return render_template("index.html")
        
        if not (operation or dip_operation or advanced_operation):
            flash("Please select at least one operation.")
            return redirect(request.url)


    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
