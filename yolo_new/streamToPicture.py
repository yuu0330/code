import cv2
import time
from datetime import datetime
import os

# 固定圖片儲存資料夾
SAVE_DIR = "stream_captures"
os.makedirs(SAVE_DIR, exist_ok=True)  # 自動建立資料夾（若不存在）

STREAM_URL = "http://pi5ca.ddns.net:5000/api/stream"

cap = None  # 預設 cap 是 None

try:
    while True:
        # 建立新的 VideoCapture 物件
        cap = cv2.VideoCapture(STREAM_URL)

        if not cap.isOpened():
            print("❌ 無法開啟串流來源，5秒後重試")
            time.sleep(5)
            continue

        ret, frame = cap.read()

        if ret:
            # 產生檔名（時間戳記）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SAVE_DIR, f"stream_{timestamp}.png")

            # 儲存圖片
            cv2.imwrite(filename, frame)
            print(f"✅ [{timestamp}] 已儲存圖片：{filename}")
        else:
            print("⚠️ 讀取畫面失敗，請檢查串流")

        # 用完記得釋放
        cap.release()
        cap = None

        # 每 300 秒（5分鐘）擷取一次
        time.sleep(300)

except KeyboardInterrupt:
    print("\n⛔ 已中止自動截圖程式")

finally:
    if cap is not None:
        cap.release()