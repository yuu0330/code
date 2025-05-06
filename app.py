from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import cv2
from ultralytics import YOLO
import requests
import random
<<<<<<< HEAD
import os
from datetime import datetime, timedelta
from flask import Response
=======
import os, io, tempfile, numpy as np
from datetime import datetime, timedelta
from flask import Response
import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import firestore
from datetime import datetime
from dateutil.parser import parse
import librosa, librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from threading import Thread
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Google Apps Script API URL
<<<<<<< HEAD
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbwMh3kIbXRs9npW8YUmsBXZwd6mcU6UrQhx6Rn4Euk3Awct_AhiQpJWv4-LqzALc_4Sag/exec"
=======
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbx9RzI9Fbs7Zgva4OxsnLCj0HHnLjuDyOfO1J8m4nT8VbHvEbeTepEI-xV8mv_APm_P/exec"
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73

# 初始化 YOLO 模型
model = YOLO("best.pt")

# 設定圖片路徑
<<<<<<< HEAD
INPUT_IMAGE_PATH = "static/斜紋夜蛾.jpg"
=======
INPUT_IMAGE_PATH = "static/237.jpg"
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
OUTPUT_IMAGE_PATH = "static/detected_pests.jpg"

# ====================== 網頁路由 ======================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/degree")
def degree():
    return render_template("degree.html")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/material")
def material():
    return render_template("material.html")

@app.route("/material_history")
def material_history():
    return render_template("material_history.html")

@app.route("/results_history")
def results_history():
    return render_template("results_history.html")

<<<<<<< HEAD
=======
@app.route("/material_analyze")
def material_analyze():
    return render_template("material_analyze.html")

>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
# 這裡只保留一個 degree_history
@app.route("/degree_history")
def degree_history():
    return render_template("degree_history.html")

<<<<<<< HEAD
=======
@app.route("/wingbeat_analysis")
def wingbeat_analysis():
    return render_template("wingbeat_analysis.html")

>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
# ====================== 環境溫濕度 API ======================
@app.route("/weather_proxy")
def weather_proxy():
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"
    params = {
        "Authorization": "CWA-233147B7-C268-43C1-BC20-C819EE149C00",
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # 抓 records 裡的 Station
        stations = data.get("records", {}).get("Station", [])
        # for station in stations:
        #     print("[Debug] TownName:", station.get("GeoInfo", {}).get("TownName"))

        # 用 GeoInfo > TownName 找
        target_station = next((station for station in stations 
                               if station.get("GeoInfo", {}).get("TownName") == "萬巒鄉"), None)

        if not target_station:
            raise ValueError("找不到萬巒鄉資料")

        weather_now = target_station.get("WeatherElement", {})
        temp = weather_now.get("AirTemperature")
        humd = weather_now.get("RelativeHumidity")

        if temp is None or humd is None:
            raise ValueError("萬巒鄉缺少溫濕度資料")

        temp = float(temp)
        humd = float(humd)

        return jsonify({
            "temperature": temp,
            "humidity": humd
        })

    except Exception as e:
        print("[Error] 氣象 API 錯誤：", e)
        return jsonify({
            "temperature": 25.0,
            "humidity": 60.0
        })

<<<<<<< HEAD
=======
# 初始化 Firebase（只做一次）
cred = credentials.Certificate("environmentdata-52a5e-firebase-adminsdk-ahqaa-8c0f279ed1.json")  # JSON 憑證檔
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://environmentdata-52a5e-default-rtdb.firebaseio.com/'
})
@app.route("/firebase_latest_data")
def firebase_latest_data():
    try:
        ref = db.reference("environmentdata/test/data")
        all_data = ref.get()

        if not all_data:
            return jsonify({"error": "Firebase 無資料"}), 404

        # 取出最新一筆（照 timestamp 排序）
        sorted_data = sorted(all_data.items(), key=lambda x: x[1].get("timestamp", ""))
        latest_entry = sorted_data[-1][1]

        return jsonify(latest_entry)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/latest_environment")
def latest_environment():
    try:
        ref = db.reference('test/data')
        data = ref.get()
        if not data:
            return jsonify({"error": "無資料"}), 404

        latest_key = sorted(data.keys())[-1]
        latest_data = data[latest_key]

        return jsonify(latest_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
# ====================== 農藥使用紀錄 API ======================
# ====================== 資材紀錄提交 API ======================
@app.route("/submit_material", methods=["POST"])
def submit_material():
    """提交資材使用紀錄到 Google Sheets"""
    try:
        # 用 JSON 方式接收資料（因為你是 POST json=data）
        data = request.json
        print("[Debug] 接收到資料：", data)

        # 補上動作類型
        data["action"] = "add_material"

        # 送到 Google Apps Script
        response = requests.post(
            GOOGLE_SHEET_API,
            json=data,
            headers={"Content-Type": "application/json"}
        )

        print("[Debug] Google 回應狀態碼：", response.status_code)
        print("[Debug] Google 回應內容：", response.text)

        # 回傳 Apps Script 回來的結果
        return jsonify(response.json())

    except Exception as e:
        print("[錯誤]", str(e))
        return jsonify({"success": False, "message": f"提交失敗：{str(e)}"}), 500

# ====================== 資材歷史紀錄讀取 API ======================
@app.route("/get_materials", methods=["GET"])
def get_materials():
    """取得農藥使用歷史紀錄資料（包含農作物欄位）"""
    try:
        # 加上 ?action=get_materials 參數叫 GAS 進行對應的資料讀取
        response = requests.get(GOOGLE_SHEET_API, params={"action": "get_materials"})

        # Google Sheets 回傳的資料直接轉成 JSON
        records = response.json()

        return jsonify(records)

    except Exception as e:
        print("[錯誤]", str(e))
        return jsonify({"error": f"資料讀取失敗：{str(e)}"}), 500

<<<<<<< HEAD
# ====================== 病蟲監測 API ======================

@app.route("/pest_data")
def pest_data():
    """隨機產生病蟲數據"""
    pest_count = random.randint(60, 110)
    return jsonify({"pest_count": pest_count})

@app.route("/detect_pests")
def detect_pests():
    """讀取圖片並標記病蟲位置"""
    img = cv2.imread(INPUT_IMAGE_PATH)

    results = model(img)
    for r in results:
        img = r.plot()  # 繪製 YOLO 偵測結果

    cv2.imwrite(OUTPUT_IMAGE_PATH, img)  # 儲存處理後的圖片
=======
# ====================== ICM分析 ======================
@app.route("/icm_pie_data")
def icm_pie_data():
    try:
        query_date = request.args.get("date")
        if not query_date:
            return jsonify({"error": "缺少日期參數"}), 400

        # 向 Google Apps Script 請求資料
        response = requests.get(GOOGLE_SHEET_API, params={"action": "get_materials"})
        raw_data = response.json()

        # 過濾指定日期資料（時間格式為 yyyy-mm-dd hh:mm）
        data = [row for row in raw_data if row.get("time", "").startswith(query_date)]

        if not data:
            # 若無資料也要回傳空結構（0 值）避免前端錯誤
            return jsonify({
                "地點": {"無紀錄": 1},
                "農作物": {"無紀錄": 1},
                "資材": {"無紀錄": 1},
                "肥料益生菌": {"無紀錄": 1}
            })

        # 定義下拉選單中顯示的值（用於分類）
        known_places = ["A", "B", "C", "D", "右區", "黃金果區F1", "綜合果樹區F2",
                         "G1溫室1", "G2溫室2", "G3溫室3", "育苗區", "資材室或工具室", "加工室(廚房或教室)"]
        known_crops = ["茄子", "秋葵", "玉米筍", "玉米", "冬瓜", "南瓜", "莧瓜", "絲瓜",
                        "紅豆", "青花筍", "高麗菜", "青椒", "辣椒", "番茄", "洋蔥", "蔥", "番薯葉",
                        "高莖類", "白菜類", "黃金果", "芒果", "檸檬", "百香果", "火龍果", "畜禽製作物", "草莓"]
        known_materials = ["無施用", "葵無露", "亞磷酸鉀", "木醋液", "苦楝油", "苦茶粕", "硫磺合劑", "波爾多液", "蘇力菌"]
        known_fertilizers = ["無施用", "市售有機堆肥", "發酵過雞糞或鴨糞", "自製液肥(農業廢棄物)", "光合菌", "治黃葉(噴粉芽孢桿菌)", "健達力蘇力菌", "菌根菌"]

        def count_items(data, field, known_list):
            counter = {item: 0 for item in known_list}
            counter["其他"] = 0

            for row in data:
                val = row.get(field, "")
                items = [i.strip() for i in val.split(",") if i.strip()]
                for item in items:
                    if item in known_list:
                        counter[item] += 1
                    else:
                        counter["其他"] += 1

            # 避免全部都是 0，讓圖表能畫出來
            total = sum(counter.values())
            if total == 0:
                counter["無資料"] = 1

            return counter

        return jsonify({
            "地點": count_items(data, "place", known_places),
            "農作物": count_items(data, "crops", known_crops),
            "資材": count_items(data, "material", known_materials),
            "肥料益生菌": count_items(data, "fertilizer", known_fertilizers),
        })

    except Exception as e:
        print("[錯誤] ICM pie 分析錯誤：", e)
        return jsonify({"error": str(e)}), 500

# ====================== 病蟲監測 API ======================
cred_ir = credentials.Certificate("data-12d9b-firebase-adminsdk-fbsvc-41f91c7e76.json")
firestore_app = firebase_admin.initialize_app(cred_ir, name="ir_app")
db_firestore = firestore.client(app=firestore_app)
# 抓取紅外線數量
@app.route("/ir_count_today")
def ir_count_today():
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        db_data = firestore.client(app=firestore_app)
        total_count = 0

        sub_collections = db_data.collection("ir_daily_count").document(today_str).collections()
        for sub_col in sub_collections:
            docs = sub_col.stream()
            for doc in docs:
                total_count += doc.to_dict().get("count", 0)

        return jsonify({"count": total_count})
    except Exception as e:
        print("[錯誤] ir_count_today:", e)
        return jsonify({"count": 0})

#查詢日期範圍總數量
@app.route("/ir_count_range")
def ir_count_range():
    start_str = request.args.get("startDate")
    end_str = request.args.get("endDate")

    if not start_str or not end_str:
        return jsonify({"error": "請提供開始與結束日期"}), 400

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        return jsonify({"error": "日期格式錯誤"}), 400

    try:
        db_data = firestore.client(app=firestore_app)
        docs = db_data.collection("Pi5_01_IR_sl").stream()
    except Exception as e:
        print("[錯誤] Firestore 連線失敗：", e)
        return jsonify({"error": "Firestore 連線失敗"}), 500

    count = 0
    for doc in docs:
        data = doc.to_dict()
        ts_str = data.get("timestamp")
        # 如果有 type 欄位需篩選，可啟用這行：
        # if data.get("type") != "IR_sl":
        #     continue

        if not ts_str:
            continue

        try:
            ts = parse(ts_str)
        except Exception as e:
            print(f"[解析錯誤] timestamp: {ts_str}，錯誤: {e}")
            continue

        if start_date <= ts < end_date:
            count += 1

    return jsonify({"count": count})
#yolo標記框
@app.route("/detect_pests")
def detect_pests():
    """讀取圖片並手動繪製 ID 編號與總數"""
    img = cv2.imread(INPUT_IMAGE_PATH)

    results = model(img)
    count = 0

    for r in results:
        boxes = r.boxes
        for i, box in enumerate(boxes):
            count += 1
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            label = f"ID: {i+1}"

            # 畫框
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # 畫 ID 字（加大字體與粗細）
            cv2.putText(
                img,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.8,              # 字體加大
                (0, 255, 0),
                3                 # 粗細加粗
            )

    # 畫總數（字體更大一點）
    cv2.putText(
        img,
        f"count: {count}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        2.5,               # 更大字體
        (0, 0, 255),
        6                  # 更粗邊框
    )

    cv2.imwrite(OUTPUT_IMAGE_PATH, img)
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
    return send_file(OUTPUT_IMAGE_PATH, mimetype="image/jpeg")

# ====================== 使用者管理 API ======================

@app.route("/register", methods=["POST"])
def register():
    """註冊 API"""
    data = request.json
    payload = {
        "action": "register",
        "name": data.get("name"),
        "phone": data.get("phone"),
        "account": data.get("account"),
        "password": data.get("password"),
        "size": data.get("size"),
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(GOOGLE_SHEET_API, json=payload, headers=headers)

    try:
        result = response.json()
    except ValueError:
        return jsonify({"success": False, "message": "Google API 回應格式錯誤"}), 500

    return jsonify(result)

@app.route("/login", methods=["POST"])
def login():
    """登入 API，驗證帳號與密碼"""
    data = request.json
    payload = {
        "action": "login",
        "account": data.get("account"),
        "password": data.get("password"),
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(GOOGLE_SHEET_API, json=payload, headers=headers)

    try:
        result = response.json()
        return jsonify(result)
    except ValueError:
        return jsonify({"success": False, "message": "API 回應格式錯誤"}), 500

@app.route("/logout")
def logout():
    return redirect(url_for("home"))

# ====================== 病蟲歷史資料 API ======================
<<<<<<< HEAD
@app.route("/fetch_degree_history")
def fetch_degree_history():
    """模擬病蟲數量與振翅頻率的歷史數據"""
=======
# @app.route("/fetch_degree_history")
# def fetch_degree_history():
#     """模擬病蟲數量與振翅頻率的歷史數據"""
#     start_date_str = request.args.get("startDate")
#     end_date_str = request.args.get("endDate")

#     if not start_date_str or not end_date_str:
#         return jsonify({"error": "請提供開始和結束日期"}), 400

#     start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
#     end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

#     dates = []
#     amount = []
#     wingbeat_frequency = []

#     current_date = start_date
#     while current_date <= end_date:
#         dates.append(current_date.strftime("%Y-%m-%d %H:%M"))
#         amount.append(random.randint(50, 150))  # 隨機產生害蟲數量
#         wingbeat_frequency.append(random.uniform(20, 120))  # 隨機產生振翅頻率 (20Hz - 120Hz)
#         current_date += timedelta(hours=6)  # 每 6 小時取一筆數據

#     return jsonify({"dates": dates, "amount": amount, "wingbeatFrequency": wingbeat_frequency})
from dateutil.parser import parse  # 如果沒加，請放在最上面
@app.route("/fetch_degree_history")
def fetch_degree_history():
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
    start_date_str = request.args.get("startDate")
    end_date_str = request.args.get("endDate")

    if not start_date_str or not end_date_str:
        return jsonify({"error": "請提供開始和結束日期"}), 400

<<<<<<< HEAD
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    dates = []
    amount = []
    wingbeat_frequency = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d %H:%M"))
        amount.append(random.randint(50, 150))  # 隨機產生害蟲數量
        wingbeat_frequency.append(random.uniform(20, 120))  # 隨機產生振翅頻率 (20Hz - 120Hz)
        current_date += timedelta(hours=6)  # 每 6 小時取一筆數據

    return jsonify({"dates": dates, "amount": amount, "wingbeatFrequency": wingbeat_frequency})
=======
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        return jsonify({"error": "日期格式錯誤"}), 400

    try:
        db_data = firestore.client(app=firestore_app)
        raw_docs = db_data.collection("Pi5_01_IR_sl").stream()
    except Exception as e:
        print(f"[錯誤] 連接 Firestore 失敗：{e}")
        return jsonify({"error": "Firestore 連線失敗"}), 500

    events = []
    for doc in raw_docs:
        data = doc.to_dict()
        if data.get("type") != "IR_sl":
            continue

        ts_str = data.get("timestamp")
        if not ts_str:
            continue

        try:
            ts = parse(ts_str)
        except Exception as e:
            print(f"[解析錯誤] timestamp: {ts_str}，錯誤: {e}")
            continue

        if start_date <= ts < end_date:
            events.append(ts)

    # 每 2 小時分組
    grouped = {}
    for t in events:
        interval = t.replace(minute=0, second=0, microsecond=0)
        interval -= timedelta(hours=t.hour % 2)
        key = interval.strftime("%Y-%m-%d %H:%M")
        grouped[key] = grouped.get(key, 0) + 1

    if not grouped:
        # 如果查不到任何資料，預設提供一筆「0」資料避免前端錯誤
        default_time = start_date.strftime("%Y-%m-%d 00:00")
        return jsonify({
            "dates": [default_time],
            "amount": [0],
            "wingbeatFrequency": [0.0]
        })

    sorted_keys = sorted(grouped.keys())
    dates = sorted_keys
    amount = [grouped[k] for k in sorted_keys]
    wingbeat_freq = [round(random.uniform(20, 120), 2) for _ in sorted_keys]

    return jsonify({
        "dates": dates,
        "amount": amount,
        "wingbeatFrequency": wingbeat_freq
    })
>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73

# ====================== 場域歷史資料 API ======================
def fetch_cwa_weather():
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-035"
    params = {
        "Authorization": "CWA-233147B7-C268-43C1-BC20-C819EE149C00",
        "format": "JSON",
        "LocationName": "內埔鄉",
        "ElementName": "平均溫度,平均相對濕度"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # 確保有 Locations 資料
        location_data = data["records"]["Locations"][0]["Location"][0]
        elements = location_data["WeatherElement"]

        # 用 ElementName 尋找正確項目
        temp_elem = next((e for e in elements if e["ElementName"] == "平均溫度"), None)
        hum_elem = next((e for e in elements if e["ElementName"] == "平均相對濕度"), None)

        if not temp_elem or not hum_elem:
            raise ValueError("無法從 API 找到平均溫度或平均相對濕度")

        # 取第一筆時間資料的數值
        temp = float(temp_elem["Time"][0]["ElementValue"][0]["Value"])
        humidity = float(hum_elem["Time"][0]["ElementValue"][0]["Value"])

        print(f"從 API 取得溫度：{temp}°C、濕度：{humidity}%")
        return temp, humidity

    except Exception as e:
        print("氣象 API 失敗：", e)
        return 25.0, 60.0  # fallback 預設值
 
@app.route('/fetch_results_history')
def fetch_results_history():
    start_date_str = request.args.get("startDate")
    end_date_str = request.args.get("endDate")

    if not start_date_str or not end_date_str:
        return jsonify({"error": "請提供完整日期"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "日期格式錯誤"}), 400

    dates = []
    ambient_temp = []
    ambient_humidity = []
    ec_value = []
    illumination = []

    # 從 API 取得平均溫度與濕度
    avg_temp, avg_humidity = fetch_cwa_weather()

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d %H:%M"))

        ambient_temp.append(avg_temp)       # 用氣象API的值
        ambient_humidity.append(avg_humidity)
        ec_value.append(round(random.uniform(0.5, 3.5), 2))
        illumination.append(random.randint(5000, 30000))

        current_date += timedelta(hours=6)

    return jsonify({
        "dates": dates,
        "ambientTemperature": ambient_temp,
        "ambientHumidity": ambient_humidity,
        "ecValue": ec_value,
        "illumination": illumination
    })

# ====================== 蟲害總數 API ======================
@app.route("/fetch_pest_history")
def fetch_pest_history():
    """根據日期範圍返回害蟲數據"""
    start_date_str = request.args.get("startDate")
    end_date_str = request.args.get("endDate")

    if not start_date_str or not end_date_str:
        return jsonify({"error": "請提供開始和結束日期"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "日期格式錯誤"}), 400

    records = []
    current_date = start_date
    while current_date <= end_date:
        records.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "pest_count": random.randint(50, 200)
        })
        current_date += timedelta(days=1)

    return jsonify(records)

# ====================== 每日變化 ======================
@app.route("/daily_trend")
def daily_trend():
    return render_template("daily_trend.html")
@app.route("/fetch_daily_trend")
def fetch_daily_trend():
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    interval = timedelta(hours=2)

    temperature_data = []
    pest_data = []
    current = today_start

    while current <= now:  # 原本是 current + interval <= now
        time_str = current.strftime("%Y-%m-%d %H:%M")
        temperature_data.append((time_str, round(random.uniform(22, 34), 1)))
        pest_data.append((time_str, random.randint(50, 150)))
        current += interval

    # 補昨天的資料（保留不動）
    if len(temperature_data) < 10:
        yesterday = today_start - timedelta(days=1)
        for i in range(15 - len(temperature_data)):
            time_str = (yesterday + i * interval).strftime("%Y-%m-%d %H:%M")
            temperature_data.insert(0, (time_str, round(random.uniform(22, 34), 1)))
            pest_data.insert(0, (time_str, random.randint(50, 150)))

    return jsonify({
        "temperature": temperature_data,
        "pests": pest_data
    })

# ====================== 上傳資料 ======================
@app.route("/submit_environment", methods=["POST"])
def submit_environment():
    data = request.json
    data["action"] = "add_environment"

    headers = {"Content-Type": "application/json"}
    response = requests.post(GOOGLE_SHEET_API, json=data, headers=headers)

    try:
        return jsonify(response.json())
    except ValueError:
        return jsonify({"success": False, "message": "格式錯誤"}), 500

# ====================== 樹梅派 ======================
camera = cv2.VideoCapture(0)  # 0 表示 USB 攝影機或樹梅派 CSI 攝影鏡頭

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route("/one")
def video():
    return render_template("one.html")

@app.route("/video")
def one():
    return render_template("video.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stream_redirect")
def stream_redirect():
    return redirect("http://192.168.1.39:5000/api/stream")

<<<<<<< HEAD
=======
# ====================== 振翅頻率分析相關 ==================================
waveform_frames_dict = {}
spectrogram_frames_dict = {}
wingbeat_counts_dict = {}

SAMPLE_RATE = 16000
FRAME_DURATION = 1  # 每段音訊長度（秒）

def extract_audio_from_video(video_path, wav_path):
    os.system(f'ffmpeg -y -i "{video_path}" -vn -ac 1 -ar {SAMPLE_RATE} -f wav "{wav_path}"')

def analyze_wingbeat(video_id, video_path):
    if video_id in waveform_frames_dict:
        return

    waveform_frames, spectrogram_frames, wingbeat_counts = [], [], []
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name

    extract_audio_from_video(video_path, wav_path)
    audio, sr = librosa.load(wav_path, sr=SAMPLE_RATE)
    samples_per_frame = int(SAMPLE_RATE * FRAME_DURATION)
    total_frames = min(len(audio) // samples_per_frame, 5)  # 只分析前 5 秒

    for i in range(total_frames):
        chunk = audio[i * samples_per_frame:(i+1) * samples_per_frame]
        # ... (保持畫圖邏輯不變)

        # 波形圖
        fig1, ax1 = plt.subplots(figsize=(4, 2))
        librosa.display.waveshow(chunk, sr=sr, ax=ax1)
        ax1.axis('off')
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='jpeg', bbox_inches='tight', pad_inches=0)
        plt.close(fig1)
        buf1.seek(0)
        waveform_frames.append(buf1.read())

        # 頻譜圖
        S = librosa.feature.melspectrogram(y=chunk, sr=sr)
        S_dB = librosa.power_to_db(S, ref=np.max)
        fig2, ax2 = plt.subplots(figsize=(4, 2))
        librosa.display.specshow(S_dB, y_axis='mel', sr=sr, ax=ax2)
        ax2.axis('off')
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='jpeg', bbox_inches='tight', pad_inches=0)
        plt.close(fig2)
        buf2.seek(0)
        spectrogram_frames.append(buf2.read())

        wingbeat_counts.append(np.random.randint(0, 5))  # 模擬振翅次數

    waveform_frames_dict[video_id] = waveform_frames
    spectrogram_frames_dict[video_id] = spectrogram_frames
    wingbeat_counts_dict[video_id] = wingbeat_counts
    os.remove(wav_path)

@app.route("/wingbeat_analysis")
def wingbeat_analysis_page():
    return render_template("wingbeat.html")

@app.route("/wingbeat/video/<video_id>")
def wingbeat_video(video_id):
    video_path = f"static/wingbeat_videos/{video_id}.mp4"
    if not os.path.exists(video_path):
        return "影片不存在", 404
    return send_file(video_path, mimetype="video/mp4")

@app.route("/wingbeat/analyze/<video_id>")
def wingbeat_trigger_analysis(video_id):
    video_path = f"static/wingbeat_videos/{video_id}.mp4"
    if not os.path.exists(video_path):
        return "影片不存在", 404

    if video_id not in waveform_frames_dict:
        Thread(target=analyze_wingbeat, args=(video_id, video_path)).start()
        return jsonify({"message": "背景分析已啟動"})
    else:
        return jsonify({"message": "已分析過，使用快取資料"})

@app.route("/wingbeat/frame/waveform/<video_id>/<int:index>")
def wingbeat_waveform(video_id, index):
    frames = waveform_frames_dict.get(video_id, [])
    if 0 <= index < len(frames):
        return Response(frames[index], mimetype='image/jpeg')
    return "無資料", 404

@app.route("/wingbeat/frame/spectrogram/<video_id>/<int:index>")
def wingbeat_spectrogram(video_id, index):
    frames = spectrogram_frames_dict.get(video_id, [])
    if 0 <= index < len(frames):
        return Response(frames[index], mimetype='image/jpeg')
    return "無資料", 404

@app.route("/wingbeat/frame/count/<video_id>/<int:index>")
def wingbeat_count(video_id, index):
    counts = wingbeat_counts_dict.get(video_id, [])
    if 0 <= index < len(counts):
        return str(counts[index])
    return "0", 404

>>>>>>> 7723c8e0c833fa905ac92d2c4cf9a09cce4d0a73
# ====================== 啟動 Flask 伺服器 ======================

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080,debug=True)
