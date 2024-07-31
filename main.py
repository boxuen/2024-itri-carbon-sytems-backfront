import os
import threading
from io import BytesIO
from tkinter import Image

import app
import cv2
import pandas as pd
import numpy as np
import pymysql
from flask import Flask, render_template, redirect, url_for, Response, jsonify
from ultralytics import YOLO
from tracker import *
import cvzone
from PIL import Image
from flask_socketio import SocketIO,emit


app = Flask(
    __name__,
    static_url_path='',
    static_folder='./',
    template_folder='./',
)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

counter1 = []
counter2 = []
num  = 0
@app.route("/")
def get_stream_html():
    return render_template('live.html')



connect_db = pymysql.connect(host='localhost', port=3306, user='root', passwd='', charset='utf8', db='peopledb')
# 創建一個游標對象
cursor = connect_db.cursor()
model = YOLO('yolov8s.pt')




#cap = cv2.VideoCapture('3.mp4')
cap = cv2.VideoCapture(0)


#===============================#
@app.route("/stop_to_yolo",methods=['POST'])
def stop_to_yolo():
    os._exit(0);






@app.route("/PeopleCounting",methods=['POST'])
def PeopleCounting():
    global counter1, counter2, frame_to_stream, num
    my_file = open("coco.txt", "r")
    data = my_file.read()
    class_list = data.split("\n")

    count = 0
    tracker = Tracker()
    # area1 = [(450, 394), (484, 370), (1020, 425), (1020, 459)]  # RED
    # area2 = [(407, 417), (448, 392), (1020, 460), (1020, 490)]  # GREEN
    area1 = [(0, 394), (0, 370), (1020, 425), (1020, 459)]  # RED
    area2 = [(0, 430), (0, 400), (1020, 480), (1020, 500)]  # GREEN
    Co2 = 0
    people_enter = {}
    #counter1 = []
    people_exit = {}
    #counter2 = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if count % 3 != 0:
            continue
        frame = cv2.resize(frame, (1020, 500))

        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")
        list = []
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            if 'person' in c:
                list.append([x1, y1, x2, y2])
        bbox_id = tracker.update(list)
        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox
            cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 1)
            results = cv2.pointPolygonTest(np.array(area1, np.int32), (x4, y4), False)
            if results >= 0:
                people_exit[id] = (x4, y4)
            if id in people_exit:
                results1 = cv2.pointPolygonTest(np.array(area2, np.int32), (x4, y4), False)
                if results1 >= 0:
                    cv2.circle(frame, (x4, y4), 4, (255, 0, 0), -1)
                    cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                    if counter2.count(id) == 0:
                        counter2.append(id)
                        num = num + 1


            results2 = cv2.pointPolygonTest(np.array(area2, np.int32), (x4, y4), False)
            if results2 >= 0:
                people_enter[id] = (x4, y4)
            if id in people_enter:
                results3 = cv2.pointPolygonTest(np.array(area1, np.int32), (x4, y4), False)
                if results3 >= 0:
                    cv2.circle(frame, (x4, y4), 4, (255, 0, 0), -1)
                    cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                    if counter1.count(id) == 0:
                        counter1.append(id)


        cv2.polylines(frame, [np.array(area1, np.int32)], True, (0, 0, 255), 1)
        cv2.polylines(frame,
                      [np.array(area2, np.int32)], True, (0, 255, 0), 1)
        enterP = len(counter1)
        exitP = len(counter2)
        # Co2 = (exitP - enterP) * 0.02
        Co2 = round(exitP * 0.0008,4)
        # Co2 = num

        from datetime import datetime

        now = datetime.now()  # current date and time
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        cvzone.putTextRect(frame, f'Date:{date_time}', (500, 100), 2, 2)
        cvzone.putTextRect(frame, f'Co2:{Co2}', (150, 50), 2, 2)
        cvzone.putTextRect(frame, f'Enter:{enterP}', (450, 50), 2, 2)
        cvzone.putTextRect(frame, f'Exit:{exitP}', (750, 50), 2, 2)
        #cv2.imshow("PeopleCounting", frame)
        # 定義要新增到資料庫的值
        enterP = len(counter2)
        exitP = len(counter1)

        sql = f"INSERT INTO Counts (DATE, IN_NUM, OUT_NUM) VALUES ('{date_time}',{enterP},{exitP})"
        try:
            # 執行 SQL 語句
            cursor.execute(sql)
            # 提交事務
            connect_db.commit()
            print("資料新增成功")

        except Exception as e:
            # 如果發生錯誤，則回滾事務
            connect_db.rollback()
            print("資料新增失敗：", e)
        socketio.emit('update_count', {'enterP': enterP, 'exitP': exitP,'Co2':Co2})

        if cv2.waitKey(5) & 0xFF == 27:
            break


    #return redirect(url_for('video_feed'))
    cap.release()
    cv2.destroyAllWindows()
    #return "People counting completed successfully."
    return render_template('live.html', enterP=enterP, exitP=exitP, Co2=Co2)



# @app.route("/",methods=['POST'])
# def get_value_html():
#
#     enterP = enterP
#     exitP = len(counter1)
#     return render_template('live.html', enterP=enterP, exitP=exitP)







if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
