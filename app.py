from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json

app = Flask(__name__)

# 画像を保存するディレクトリ
IMAGE_FOLDER = 'static/images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ローカルストレージの代わりに画像のURLを保存するファイル
IMAGES_FILE = 'images.json'
DELETED_IMAGES_FILE = 'deleted_images.json'

# 初期化
if not os.path.exists(IMAGES_FILE):
    with open(IMAGES_FILE, 'w') as f:
        json.dump([], f)  # 空のリストを保存

if not os.path.exists(DELETED_IMAGES_FILE):
    with open(DELETED_IMAGES_FILE, 'w') as f:
        json.dump([], f)  # 空のリストを保存

# 画像リストを取得
def get_images():
    with open(IMAGES_FILE, 'r') as f:
        return json.load(f)

# 削除された画像リストを取得
def get_deleted_images():
    with open(DELETED_IMAGES_FILE, 'r') as f:
        return json.load(f)

# 画像を保存
def save_images(images):
    with open(IMAGES_FILE, 'w') as f:
        json.dump(images, f)

# 削除された画像を保存
def save_deleted_images(images):
    with open(DELETED_IMAGES_FILE, 'w') as f:
        json.dump(images, f)

@app.route('/home')  # ここを/homeに変更
def home():
    images = get_images()  # 画像リストを取得
    return render_template('home.html', images=images)

@app.route('/add_image', methods=['POST'])
def add_image():
    url = request.form['imageUrl']
    if url:
        images = get_images()
        images.append(url)  # 画像のURLをリストに追加
        save_images(images)
    return redirect(url_for('home'))

@app.route('/delete_image/<int:index>', methods=['POST'])
def delete_image(index):
    images = get_images()
    if 0 <= index < len(images):
        deleted_images = get_deleted_images()
        deleted_images.append(images[index])  # 削除された画像を保存
        save_deleted_images(deleted_images)

        images.pop(index)  # 画像を削除
        save_images(images)
    return redirect(url_for('home'))

@app.route('/deleted_images')
def deleted_images():
    deleted_images = get_deleted_images()  # 削除された画像リストを取得
    return render_template('deleted_images.html', images=deleted_images)

@app.route('/restore_image/<int:index>', methods=['POST'])
def restore_image(index):
    deleted_images = get_deleted_images()
    if 0 <= index < len(deleted_images):
        images = get_images()
        images.append(deleted_images[index])  # 画像を元に戻す
        save_images(images)

        deleted_images.pop(index)  # 削除された画像から削除
        save_deleted_images(deleted_images)
    return redirect(url_for('deleted_images'))

@app.route('/delete_permanently/<int:index>', methods=['POST'])
def delete_permanently(index):
    deleted_images = get_deleted_images()
    if 0 <= index < len(deleted_images):
        deleted_images.pop(index)  # 削除された画像を完全に削除
        save_deleted_images(deleted_images)
    return redirect(url_for('deleted_images'))

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')


if name == "main":
    from threading import Thread

    # Flaskアプリを別スレッドで実行
    flask_thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': int(os.getenv('PORT', 8080))})
    flask_thread.start()

    # Discordボットをメインスレッドで実行
