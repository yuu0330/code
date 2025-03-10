import os
import random
import shutil

# 設定來源圖片和標記檔的資料夾路徑
source_img_folder = 'C:/Users/Win11/Desktop/yolo_2/images1'
source_label_folder = 'C:/Users/Win11/Desktop/yolo_2/txt'

# 設定存放分割後資料集的資料夾路徑
dest_folder = 'C:/Users/Win11/Desktop/yolo_2/images'

# 建立 train, val, test 資料夾，每個資料夾內含 images 與 labels 子資料夾
for subset in ['train', 'val', 'test']:
    os.makedirs(os.path.join(dest_folder, subset, 'images'), exist_ok=True)
    os.makedirs(os.path.join(dest_folder, subset, 'labels'), exist_ok=True)

# 取得所有圖片檔案（假設格式為 jpg 或 png，可根據需要擴充）
images = [f for f in os.listdir(source_img_folder) if f.lower().endswith(('.jpg', '.png'))]

# 隨機打亂檔案順序
random.shuffle(images)

total = len(images)
train_end = int(total * 0.7)
val_end = train_end + int(total * 0.2)

train_images = images[:train_end]
val_images = images[train_end:val_end]
test_images = images[val_end:]

def copy_files(image_list, subset):
    for image in image_list:
        # 複製圖片
        src_img_path = os.path.join(source_img_folder, image)
        dst_img_path = os.path.join(dest_folder, subset, 'images', image)
        shutil.copy(src_img_path, dst_img_path)
        
        # 對應的標記檔名稱（假設副檔名為 .txt）
        label_filename = os.path.splitext(image)[0] + '.txt'
        src_label_path = os.path.join(source_label_folder, label_filename)
        dst_label_path = os.path.join(dest_folder, subset, 'labels', label_filename)
        if os.path.exists(src_label_path):
            shutil.copy(src_label_path, dst_label_path)
        else:
            print(f"Warning: 找不到 {src_label_path}")

# 分別將圖片及標記檔複製到 train, val, test 資料夾中
copy_files(train_images, 'train')
copy_files(val_images, 'val')
copy_files(test_images, 'test')

print("資料集分割完成！")
