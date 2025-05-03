import os
from PIL import Image

PATH = r"C:/Users/Win11/Desktop/web/code-1/yolo_new/img"

def convert_png_to_jpg(path):
    new_files = []

    for file in sorted(os.listdir(path)):
        full_path = os.path.join(path, file)
        name, ext = os.path.splitext(file)
        ext = ext.lower()

        if os.path.isfile(full_path):
            if ext == '.png':
                try:
                    img = Image.open(full_path).convert("RGB")
                    temp_jpg_name = name + "_converted_temp.jpg"  # 使用暫時名稱避免衝突
                    temp_jpg_path = os.path.join(path, temp_jpg_name)
                    img.save(temp_jpg_path, "JPEG")
                    os.remove(full_path)
                    new_files.append(temp_jpg_path)
                except Exception as e:
                    print(f"轉換 {file} 發生錯誤: {e}")
            elif ext == '.jpg':
                new_files.append(full_path)

    return new_files

def rename_images_to_sequential_jpg(files):
    # 排序後，先用暫時名稱避免衝突
    temp_map = []
    for idx, file_path in enumerate(sorted(files)):
        temp_name = f"temp_rename_{idx}.jpg"
        temp_path = os.path.join(os.path.dirname(file_path), temp_name)
        os.rename(file_path, temp_path)
        temp_map.append(temp_path)

    # 第二階段正式命名為 0.jpg, 1.jpg, ...
    for idx, temp_path in enumerate(temp_map):
        final_name = f"{idx}.jpg"
        final_path = os.path.join(os.path.dirname(temp_path), final_name)
        os.rename(temp_path, final_path)
        print(f"{os.path.basename(temp_path)} → {final_name}")

if __name__ == '__main__':
    all_jpgs = convert_png_to_jpg(PATH)
    rename_images_to_sequential_jpg(all_jpgs)
