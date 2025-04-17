from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import cv2
from ultralytics import YOLO
import requests
import random
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Google Apps Script API URL
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycby_tt0I_ot4Yp_GW12j6TfIOZUS9Tskq-Ak5Kq9FlDOVz7UnQwIP13J2Q_2n1pwq46R6Q/exec"

# 氣象 API 設定
# API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-035"
# API_KEY = "CWA-233147B7-C268-43C1-BC20-C819EE149C00"
# LOCATION_NAME = "內埔鄉"
# ELEMENTS = "平均溫度,平均相對濕度"

# 初始化 YOLO 模型
model = YOLO("best.pt")

# 設定圖片路徑
INPUT_IMAGE_PATH = "static/斜紋夜蛾.jpg"
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

# 這裡只保留一個 degree_history
@app.route("/degree_history")
def degree_history():
    return render_template("degree_history.html")

# ====================== 農藥使用紀錄 API ======================
@app.route("/submit_material", methods=["POST"])
def submit_material():
    """提交農藥使用紀錄到 Google 試算表"""
    data = request.form.to_dict()
    data["action"] = "add_material"

    response = requests.post(GOOGLE_SHEET_API, json=data, headers={"Content-Type": "application/json"})

    try:
        result = response.json()
    except ValueError:
        return jsonify({"success": False, "message": "API 回應格式錯誤"}), 500

    return jsonify(result)

# 只保留一個 `get_materials`
@app.route("/get_materials", methods=["GET"])
def get_materials():
    """獲取農藥使用歷史紀錄 (確保 `time` 顯示正確)"""
    response = requests.get(GOOGLE_SHEET_API, params={"action": "get_materials"})

    try:
        records = response.json()
    except ValueError:
        return jsonify({"error": "API 回應格式錯誤"}), 500

    return jsonify(records)

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
@app.route("/fetch_degree_history")
def fetch_degree_history():
    """模擬病蟲數量與振翅頻率的歷史數據"""
    start_date_str = request.args.get("startDate")
    end_date_str = request.args.get("endDate")

    if not start_date_str or not end_date_str:
        return jsonify({"error": "請提供開始和結束日期"}), 400

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

# ====================== 場域歷史資料 API ======================
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
    temperature = []
    humidity = []
    soil_temp = []
    soil_moisture = []
    ec_value = []

    # 生成隨機數據
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d %H:%M"))
        temperature.append(random.uniform(20, 35))  # 環境溫度
        humidity.append(random.uniform(40, 80))  # 環境濕度
        soil_temp.append(random.uniform(15, 30))  # 土壤溫度
        soil_moisture.append(random.uniform(10, 50))  # 土壤含水量
        ec_value.append(random.uniform(0.5, 2.0))  # EC 值
        current_date += timedelta(hours=6)

    return jsonify({
        "dates": dates,
        "ambientTemperature": temperature,
        "ambientHumidity": humidity,
        "soilTemperature": soil_temp,
        "soilMoisture": soil_moisture,
        "ecValue": ec_value
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
    """回傳今日或昨日每兩小時的溫度與蟲數資料，最多15筆"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    interval = timedelta(hours=2)

    temperature_data = []
    pest_data = []
    current = today_start

    while current <= now and len(temperature_data) < 15:
        time_str = current.strftime("%Y-%m-%d %H:%M")
        temperature_data.append((time_str, round(random.uniform(22, 34), 1)))
        pest_data.append((time_str, random.randint(50, 150)))
        current += interval

    # 如果資料太少就補昨天的
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

# ====================== 啟動 Flask 伺服器 ======================

if __name__ == "__main__":
    app.run(debug=True)
