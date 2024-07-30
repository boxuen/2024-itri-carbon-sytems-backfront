# 建立連接
from datetime import time

import pymysql

from main import date_time, counter2, counter1

connect_db = pymysql.connect(host='localhost', port=3306, user='root', passwd='', charset='utf8', db='peopledb')

# 創建一個游標對象
cursor = connect_db.cursor()

# 定義要新增到資料庫的值
enterP = len(counter1)
exitP = len(counter2)

# 輸出格式化後的時間
# 定義插入資料的 SQL 語句
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
    time.sleep(60)
# 關閉游標和連接
cursor.close()
connect_db.close()