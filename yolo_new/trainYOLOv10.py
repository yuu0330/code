from ultralytics import YOLO
import torch

# 釋放顯示卡快取，避免記憶體爆掉
torch.cuda.empty_cache()

if __name__ == '__main__':

    # 載入 YOLO 模型
    model = YOLO('yolov9c.pt')  

    # 訓練模型
    model.train(
        data='C:/Users/Win11/Desktop/web/code-1/yolo_new/Data.yaml',
        epochs=100,              # 訓練總輪數（epoch 數越多訓練越久）
        imgsz=640,               # 輸入圖片尺寸（常見為 640，可根據模型與 GPU 調整）
        device=0,                # 使用哪張 GPU（0 表第 1 張，改成 "cpu" 則用 CPU 訓練）
        workers=8,               # 數據加載執行緒數（越多載圖越快，需視 CPU 而定）
        lr0=0.005,               # 初始學習率（學習率大小會影響收斂速度與穩定性）
        batch=4,                 # 每次訓練的批次數（越大訓練越快，但吃更多 GPU RAM）
        dropout=0.2,             # dropout 機率（防止過擬合，可選項）
        warmup_epochs=3,         # 熱身輪數（前幾輪會使用較小學習率，避免梯度爆炸）
        val=True                 # 每個 epoch 是否執行驗證（建議保持 True）
        # optimizer='SGD'        # ← 可選項。若穩定性重要可用 SGD，否則預設是 AdamW
    )
