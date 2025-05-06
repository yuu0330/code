import glob
import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

PATH='C:/Users/Win11/Desktop/yolo_2/reSize'

imgs = glob.glob(PATH+'/*')
os.makedirs('reSize', exist_ok=True)
for i in imgs:
    im = Image.open(i)
    size = im.size
    name = i.split('\\')[::-1][0]        # 取得圖片名稱
    print(name)
    if im.mode == 'RGBA':
        im = im.convert('RGB')
    im2 = im.resize((1280, 1280))         # 調整圖片尺寸
    im2.save(f'reSize/{name}')   # 調整後存檔到 reSize 資料夾