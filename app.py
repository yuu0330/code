from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import cv2
from ultralytics import YOLO
import requests
import random
import os
from datetime import datetime, timedelta
from flask import Response

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Google Apps Script API URL
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbz53huxpRaJCt-Eb0aXMzzVm2Iyh_BWTLzlgNZAdwbSf16HFZw1zhDtpRlqtrpwZrFsMw/exec"

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

# ====================== 環境溫濕度 API ======================
@app.route("/weather_proxy")
def weather_proxy():
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-035"
    params = {
        "Authorization": "CWA-233147B7-C268-43C1-BC20-C819EE149C00",
        "format": "JSON",
        "LocationName": "內埔鄉",
        "ElementName": "平均溫度,平均相對濕度"
    }

    try:
        response = requests.get(url, params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ====================== 農藥使用紀錄 API ======================
@app.route("/submit_material", methods=["POST"])
def submit_material():
    try:
        data = request.form.to_dict()
        print("[Debug] 接收到資料：", data)

        data["action"] = "add_material"

        response = requests.post(
            "https://script.google.com/macros/s/AKfycbz53huxpRaJCt-Eb0aXMzzVm2Iyh_BWTLzlgNZAdwbSf16HFZw1zhDtpRlqtrpwZrFsMw/exec",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        print("[Debug] Google 回應狀態碼：", response.status_code)
        print("[Debug] Google 回應內容：", response.text)

        return jsonify(response.json())
    except Exception as e:
        print("[錯誤]", str(e))
        return jsonify({"success": False, "message": f"提交失敗：{str(e)}"}), 500

@app.route("/get_materials", methods=["GET"])
def get_materials():
    """取得農藥使用歷史紀錄資料"""
    try:
        response = requests.get(GOOGLE_SHEET_API, params={"action": "get_materials"})
        records = response.json()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": f"資料讀取失敗：{str(e)}"}), 500
    
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
    """回傳今日或昨日每兩小時的溫度與蟲數資料，最多15筆"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    interval = timedelta(hours=2)

    temperature_data = []
    pest_data = []
    current = today_start

    while current + interval <= now and len(temperature_data) < 15:
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

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stream_redirect")
def stream_redirect():
    return redirect("http://192.168.178.153:5000/api/stream")

# ====================== 啟動 Flask 伺服器 ======================

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080,debug=True)
