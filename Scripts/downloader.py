import os
import shutil
import json
import hashlib
from typing import List
from datetime import datetime
import pytz
import platform
import zipfile
from network import download_file, get_hashfile_url

history_path = 'history'
andorid_hash_url = "https://line3-patch-blhx.bilibiligame.net/android/hash/"
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

def latest_history() -> str:
    """
    获取最新的history文件夹
    """
    history_list = os.listdir(history_path)
    history_list.sort()
    return os.path.join(history_path, history_list[-1])

def file_hash(filepath):
    """计算文件的哈希值"""
    hash_algo = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def compare_files(file1, file2):
    """比较两个文件是否一样"""
    return file_hash(file1) == file_hash(file2)

def extract_folder_from_apk(apk_path: str, folder_in_apk: str, extract_to: str) -> None:
    with zipfile.ZipFile(apk_path, 'r') as apk:
        for file_info in apk.infolist():
            if file_info.filename.startswith(folder_in_apk):
                apk.extract(file_info, extract_to)
            
def get_md5(file_path: str) -> str:
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()

def get_hash_from_apk(apk_version: str) -> None:
    """获取apk文件中的hash值"""
    if platform.system() == "Linux":
        os.system(f"wget -O tmp/base.apk {apk_version}")
    elif platform.system() == "Windows":
        os.system(f"powershell -Command \"Invoke-WebRequest -Uri {apk_version} -OutFile tmp\\base.apk\"")

    extract_folder_from_apk('tmp/base.apk', 'assets/AssetBundles/', 'tmp')

    with open('hashes-apk.csv', 'w', encoding='utf-8') as f:
        base_path = 'tmp/assets/AssetBundles/'
        for root, dirs, files in os.walk(base_path):
            mroot = root.replace(base_path, '').replace('\\', '/')
            for file in files:
                key = (mroot == '') and file or f'{mroot}/{file}'
                md5 = get_md5(os.path.join(root, file))
                size = os.path.getsize(os.path.join(root, file))
                f.write(f'{key},{size},{md5}\n')
        

if __name__ == "__main__":
    os.mkdir('tmp')
    last = latest_history()
    apk_version, hashfile_url = get_hashfile_url()
    data = {
        'apk_version': apk_version,
        'hashfile_url': hashfile_url
    }
    with open('tmp/version.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    if not compare_files('tmp/version.json', f'{last}/version.json'):
        for key, value in hash_csv_name.items():
            download_file(f'{andorid_hash_url}{hashfile_url[key]}', 'tmp', value)
        with open(f'{latest_history()}/version.json', 'r', encoding='utf-8') as f:
            old_apk_version = json.load(f)['apk_version']
            if old_apk_version != apk_version:
                get_hash_from_apk(apk_version)
    elif not os.path.exists(f'hashes-apk.csv'):
        get_hash_from_apk(apk_version)
    else:
        shutil.rmtree('tmp')
        print("No changes.")
        exit()

    beijing_tz = pytz.timezone('Asia/Shanghai')
    date = datetime.now(beijing_tz).strftime('%Y-%m-%d-%H-%M')
    path = os.path.join(history_path, date)
    os.mkdir(path)
    for file in os.listdir('tmp'):
        shutil.copy(os.path.join('tmp', file), os.path.join(path, file))
        shutil.copy(os.path.join('tmp', file), file)

    shutil.rmtree('tmp')
    print(date)