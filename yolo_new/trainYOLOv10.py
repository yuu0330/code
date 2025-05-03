from ultralytics import YOLO
import torch
torch.cuda.empty_cache()
if __name__ == '__main__':
        
    # 加载模型
    model = YOLO('yolov10x.pt')

    # 訓練
    model.train(
        data='Data.yaml', # 訓練配置文件
        epochs=100, # 訓練的次數
        patience=10,  # 早停策略，防止過擬合
        imgsz=640, # 輸入影像大小，可調整為 320、640、1024、1280，解析度越高效果越好但訓練更慢
        device=0,   # 使用的設備編號（0 代表 GPU，"cpu" 代表使用 CPU）
        workers=8, # 資料加載的線程數量，視CPU性能調整，建議設置的值為CPU實體核心數的1-2倍
        lr0=0.0025, # 初始學習率，視情況調整（小模型、大資料集用高學習率，大模型、小資料集用低學習率）
        lrf=0.01,  # 最終學習率
        batch=4,    # 批次大小(根據 GPU 記憶體、資料集大小調整)
        dropout=0.1,  # 避免過度正則化
        warmup_epochs=5,  # 增加 warmup 讓學習率平滑提升
    )
