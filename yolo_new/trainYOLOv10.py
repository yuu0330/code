from ultralytics import YOLO
import torch
torch.cuda.empty_cache()
if __name__ == '__main__':
        
    # 加载模型
    model = YOLO('yolov10x.pt')

    # 訓練
    model.train(
        data='BD_SL.yaml', # 訓練配置文件
        epochs=100, # 訓練的次數
        imgsz=640, # 輸入影像大小，可調整為 320、640、1024、1280，解析度越高效果越好但訓練更慢
        device=0,   # 使用的設備編號（0 代表 GPU，"cpu" 代表使用 CPU）
        workers=8, # 資料加載的線程數量，視CPU性能調整，建議設置的值為CPU實體核心數的1-2倍
        lr0=0.005, # 學習率，視情況調整（小模型、大資料集用高學習率，大模型、小資料集用低學習率）
        batch=4,    # 批次大小(根據 GPU 記憶體、資料集大小調整)
        dropout=0.2,
        #optimizer='SGD',        # 若要穩健訓練，SGD 較穩；AdamW 速度快但波動較大
        warmup_epochs=3,        # 增加穩定性
        val=True,               # 每輪驗證
    )
