import os
import shutil
import json
import hashlib
from typing import List
from datetime import datetime

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

    date = datetime.now().strftime('%Y-%m-%d-%H-%M')
    path = os.path.join(history_path, date)
    os.mkdir(path)
    for file in os.listdir('tmp'):
        shutil.copy(os.path.join('tmp', file), os.path.join(path, file))
        shutil.copy(os.path.join('tmp', file), file)

    shutil.rmtree('tmp')