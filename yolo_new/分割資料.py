import os
import shutil
from tqdm import tqdm

# 圖片位置
image_dir = "0426to29_increaseImg"
# 標記位置
label_dir = "0426to29_txt"
# 訓練集的比例(90%訓練集，10%驗證集)
training_ratio = 0.9
# 拆分後，資料的位置
train_dir = "train_data"

def split_data():
    list = os.listdir(image_dir)
    all = len(list)
    train_count = int(all * training_ratio)
    train_images = list[0:train_count]
    val_images = list[train_count:]

    # 訓練集目錄
    os.makedirs(os.path.join(train_dir, "images/train"), exist_ok=True)
    os.makedirs(os.path.join(train_dir, "labels/train"), exist_ok=True)
    # 驗證集目錄
    os.makedirs(os.path.join(train_dir, "images/val"), exist_ok=True)
    os.makedirs(os.path.join(train_dir, "labels/val"), exist_ok=True)

    # 訓練集
    with open(os.path.join(train_dir, "train.txt"), "w") as file:
        file.write("\n".join([train_dir + "images/train/" + image_file for image_file in train_images]))
    print("save train.txt success!")
    # 複製資料
    for item in tqdm(train_images):
        label_file = item.replace(".png", ".txt")
        shutil.copy(os.path.join(image_dir, item), os.path.join(train_dir, "images/train/"))
        shutil.copy(os.path.join(label_dir, label_file), os.path.join(train_dir, "labels/train/"))

    # 驗證集
    with open(os.path.join(train_dir, "val.txt"), "w") as file:
        file.write("\n".join([train_dir + "images/val/" + image_file for image_file in val_images]))
    print("save val.txt success!")
    # 複製資料
    for item in tqdm(val_images):
        label_file = item.replace(".png", ".txt")
        shutil.copy(os.path.join(image_dir, item), os.path.join(train_dir, "images/val/"))
        shutil.copy(os.path.join(label_dir, label_file), os.path.join(train_dir, "labels/val/"))


if __name__ == '__main__':
    split_data()