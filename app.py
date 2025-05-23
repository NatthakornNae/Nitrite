from flask import Flask, request, render_template, send_from_directory
import cv2
import numpy as np
import os
import base64
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def analyze_nitrite_level(image_path, mode="yellow"):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (200, 200))
    b, g, r = cv2.mean(img)[:3]  

    if mode == "white":
        PCON = g - 248.63
        CON_ppm = abs(PCON / 35.433)
    else:  # yellow
        PCON = g - 208.23
        CON_ppm = abs(PCON / 77.37)

    CON_mg_ml = CON_ppm / 1000
    return f"ปริมาณไนไตรต์โดยประมาณ: {CON_mg_ml:.4f} mg/mL ({'ฉี่ใส' if mode == 'white' else 'ฉี่เหลือง'})"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    mode = request.form.get('mode', 'yellow')  # ค่า default คือ yellow

    if 'image' in request.files:
        file = request.files['image']
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
    else:
        data_url = request.form['camera_image']
        header, encoded = data_url.split(",", 1)
        binary_data = base64.b64decode(encoded)
        filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(binary_data)

    result = analyze_nitrite_level(filepath, mode)
    return render_template('result.html', image_url=f'/uploads/{filename}', result=result)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18800)
