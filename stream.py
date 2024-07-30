import cv2
import cvzone
import numpy as np
import pandas as pd
from flask import Flask, render_template, Response
from io import BytesIO
from PIL import Image
from ultralytics import YOLO

from tracker import *

app = Flask(
    __name__,
    static_url_path='',
    static_folder='./',
    template_folder='./',
)


@app.route("/", methods=['GET'])
def get_stream_html():
    return render_template('live.html')


def resize_img_2_bytes(image, resize_factor, quality):
    bytes_io = BytesIO()
    img = Image.fromarray(image)

    w, h = img.size
    img.thumbnail((int(w * resize_factor), int(h * resize_factor)))
    img.save(bytes_io, 'jpeg', quality=quality)

    return bytes_io.getvalue()
def get_image_bytes():
    # 從視訊擷取裝置讀取影像
    success, img = cap.read()
    if success:
        # 將影像轉換為 RGB 格式
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 將影像大小調整為原來的 50%，並將品質設定為 30
        img_bytes = resize_img_2_bytes(img, resize_factor=0.5, quality=30)
        # 如果成功讀取影像，則返回影像的位元組
        return img_bytes

    # 如果讀取影像失敗，則返回 None
    return None


def gen_frames():
    while True:
        img_bytes = get_image_bytes()
        if img_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_bytes + b'\r\n')


@app.route('/api/stream')
def video_stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# def get_image_bytes():
#     success, img = cap.read()
#     if success:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         img_bytes = resize_img_2_bytes(img, resize_factor=0.5, quality=30)
#         return img_bytes
#
#     return None
cap = cv2.VideoCapture("2.mkv")




if __name__ == "__main__":
    app.run(host='0.0.0.0')




