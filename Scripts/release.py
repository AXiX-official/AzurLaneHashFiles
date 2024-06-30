import zipfile
import sys

hash_csv_name = {
    'az': 'hashes.csv',
    'cv': 'hashes-cv.csv',
    'l2d': 'hashes-live2d.csv',
    'pic': 'hashes-pic.csv',
    'bgm': 'hashes-bgm.csv',
    'painting': 'hashes-painting.csv',
    'manga': 'hashes-manga.csv',
    'cipher': 'hashes-cipher.csv'
}

if __name__ == "__main__":
    name = sys.argv[1]
    with zipfile.ZipFile(f"{name}.zip", 'w') as myzip:
        for key, file_name in hash_csv_name.items():
            myzip.write(file_name)
        myzip.write('version.json')