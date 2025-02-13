from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder to store uploaded images
UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/results/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image
        process_image(filepath, filename)

        return render_template('result.html',
                               original_image=url_for('static', filename='uploads/' + filename),
                               grayscale_image=url_for('static', filename='results/gray_' + filename),
                               binary_image=url_for('static', filename='results/binary_' + filename),
                               contour_image=url_for('static', filename='results/contour_' + filename))
    else:
        return redirect(request.url)

def process_image(filepath, filename):
    # Read and process the image
    image = cv2.imread(filepath)
    image = cv2.resize(image, None, fx=0.9, fy=0.9)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(binary, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    # Save grayscale image
    gray_path = os.path.join(app.config['RESULT_FOLDER'], 'gray_' + filename)
    cv2.imwrite(gray_path, gray)

    # Save binary image
    binary_path = os.path.join(app.config['RESULT_FOLDER'], 'binary_' + filename)
    cv2.imwrite(binary_path, binary)

    # Draw contours on the original image
    contour_image = image.copy()
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    # Save contour image
    contour_path = os.path.join(app.config['RESULT_FOLDER'], 'contour_' + filename)
    cv2.imwrite(contour_path, contour_image)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    app.run(debug=True)
