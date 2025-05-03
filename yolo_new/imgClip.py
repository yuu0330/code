import glob
import os
from PIL import Image

PATH='C:/Users/Win11/Desktop/yolo_2/test'

def image_clip(name,filename, width_scale, height_scale):
    image = Image.open(filename)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    (width, height), (_width, _height) = image.size, image.size
    _height = width / width_scale * height_scale
    if _height > height:
        _height = height
        _width = width_scale * height / height_scale
    image.crop((0, 0, _width, _height)).save(f"reClip/{name}_L.jpg")  # 從左上角開始切
    image.crop((width - _width, 0, width, _height)).save(f"reClip/{name}_R.jpg")  # 從右上角開始切

if __name__ == '__main__':
    os.makedirs('reClip', exist_ok=True)
    imgs = glob.glob(PATH+'/*')
    for filename in imgs:
        name = filename.split('\\')[::-1][0].split('.')[0]
        image_clip(name,filename, width_scale=1, height_scale=1)