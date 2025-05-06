import os

PATH="C:/Users/Win11/Desktop/yolo_2/test"

def deal(path):
    file_names = os.listdir(path)
    c = 0
    for file in file_names:
        suffix = file.split('.')[-1]
        os.rename(os.path.join(path, file), os.path.join(path, '{:0>6d}.{}'.format(c, suffix)))
        c += 1
        
def deal2(path):
    file_names = os.listdir(path)
    c = 0
    for file in file_names:
        suffix = file.split('.')[-1]
        os.rename(os.path.join(path, file), os.path.join(path, '{}.{}'.format(c, suffix)))
        c += 1

if __name__ == '__main__':
    deal(PATH)
    deal2(PATH)  

