# By Andrés Sánchez Serrano
from flask import Flask, render_template, request, redirect, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, datetime
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

app = Flask(__name__)
auth = HTTPBasicAuth()

# Credenciales
users = {"admin": generate_password_hash("boitaull2025")}

@auth.verify_password
def verify_password(username, password):
    return username in users and check_password_hash(users[username], password)

# Constantes
DATA_FILE = 'db.json'
QR_FOLDER = 'static/qrs'
UPLOAD_FOLDER = 'static/uploads'
FONT_PATH = 'static/fonts/Lobster-Regular.ttf'
DOMAIN = 'https://qr.boitaullresort.com/qr'

# Funciones de base de datos
def load_db():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_db(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def ajustar_fuente(texto, max_ancho, font_path, tamaño_inicial=40):
    tamaño = tamaño_inicial
    while tamaño > 10:
        font = ImageFont.truetype(font_path, tamaño)
        w = font.getbbox(texto)[2]
        if w <= max_ancho:
            return font
        tamaño -= 2
    return ImageFont.truetype(font_path, 10)

# Generador visual de QR
def generar_qr(id, name, url, text_bottom='', text_center=''):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(f"{DOMAIN}/{id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_size = img.size[0]

    logo_path = os.path.join(UPLOAD_FOLDER, f"center_{id}.png")
    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            logo_img.thumbnail((100, 100), Image.LANCZOS)
            pos = ((qr_size - logo_img.size[0]) // 2, (qr_size - logo_img.size[1]) // 2)
            img.paste(logo_img, pos, logo_img)
        except Exception as e:
            print(f"[{id}] ⚠️ Error al procesar logo: {e}")

    draw = ImageDraw.Draw(img)
    if text_center:
        font_center = ajustar_fuente(text_center, qr_size - 40, FONT_PATH)
        bbox = font_center.getbbox(text_center)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((qr_size - w) / 2, (qr_size - h) / 2), text_center, font=font_center, fill="black")

    if text_bottom:
        new_img = Image.new("RGB", (img.size[0], img.size[1] + 60), "white")
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        font_bottom = ImageFont.truetype(FONT_PATH, 40)
        bbox = font_bottom.getbbox(text_bottom)
        w = bbox[2] - bbox[0]
        draw.text(((new_img.size[0] - w) / 2, img.size[1] + 5), text_bottom, font=font_bottom, fill="black")
        img = new_img

    os.makedirs(QR_FOLDER, exist_ok=True)
    img.save(f"{QR_FOLDER}/{id}.png")

# Ruta principal
@app.route('/')
@auth.login_required
def index():
    data = load_db()
    qrs = {k: v for k, v in data.items() if v.get("tipo") != "wifi"}
    wifis = {k: v for k, v in data.items() if v.get("tipo") == "wifi"}
    return render_template('index.html', data=qrs, wifis=wifis)

# Crear QR visual
@app.route('/new', methods=['GET', 'POST'])
@auth.login_required
def new():
    if request.method == 'POST':
        data = load_db()
        new_id = str(max([int(k) for k in data.keys()] + [0]) + 1)
        name = request.form['name']
        url = request.form['url']
        text_bottom = request.form.get('text_bottom', '')
        text_center = request.form.get('text_center', '')
        logo_file = request.files.get('logo')

        if logo_file and logo_file.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            logo_path = os.path.join(UPLOAD_FOLDER, f"center_{new_id}.png")
            logo_file.save(logo_path)

        data[new_id] = {
            "name": name,
            "url": url,
            "text_bottom": text_bottom,
            "text_center": text_center,
            "visitas": 0,
            "dispositivos": [],
            "tipo": "normal"
        }

        generar_qr(new_id, name, url, text_bottom, text_center)
        save_db(data)
        return redirect('/')
    return render_template('new.html')

# Crear QR WiFi
@app.route('/wifi', methods=['GET', 'POST'])
@auth.login_required
def new_wifi():
    if request.method == 'POST':
        data = load_db()
        new_id = str(max([int(k) for k in data.keys()] + [0]) + 1)
        ssid = request.form['ssid']
        password = request.form['password']
        security = request.form['security']

        qr_content = f"WIFI:T:{security};S:{ssid};P:{password};;"
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        os.makedirs(QR_FOLDER, exist_ok=True)
        img.save(f"{QR_FOLDER}/{new_id}.png")

        data[new_id] = {
            "name": f"WiFi {ssid}",
            "url": "#",
            "text_bottom": f"Red: {ssid}",
            "text_center": "WiFi",
            "visitas": 0,
            "dispositivos": [],
            "tipo": "wifi"
        }
        save_db(data)
        return redirect('/')
    return render_template('new_wifi.html')

# Editar QR
@app.route('/edit/<id>', methods=['GET', 'POST'])
@auth.login_required
def edit(id):
    data = load_db()
    if id not in data:
        return "QR no encontrado", 404

    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        text_bottom = request.form.get('text_bottom', '')
        text_center = request.form.get('text_center', '')
        logo_file = request.files.get('logo')

        data[id].update({
            "name": name,
            "url": url,
            "text_bottom": text_bottom,
            "text_center": text_center,
        })

        if logo_file and logo_file.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            logo_path = os.path.join(UPLOAD_FOLDER, f"center_{id}.png")
            logo_file.save(logo_path)

        generar_qr(id, name, url, text_bottom, text_center)
        save_db(data)
        return redirect('/')
    return render_template('edit.html', id=id, **data[id])

# Borrar QR
@app.route('/delete/<id>', methods=['POST'])
@auth.login_required
def delete(id):
    data = load_db()
    if id in data:
        for file in [f"{QR_FOLDER}/{id}.png", f"{UPLOAD_FOLDER}/center_{id}.png"]:
            if os.path.exists(file):
                os.remove(file)
        del data[id]
        save_db(data)
    return redirect('/')

# Estadísticas
@app.route('/stats/<id>')
@auth.login_required
def stats(id):
    data = load_db()
    if id not in data:
        return "QR no encontrado", 404
    return render_template('stats.html', id=id, qr=data[id])

# Contador + redirección
@app.route('/qr/<id>')
def redirect_qr(id):
    data = load_db()
    if id in data:
        data[id]["visitas"] = data[id].get("visitas", 0) + 1
        user_agent = request.headers.get("User-Agent", "desconocido")
        now = datetime.datetime.now().isoformat()
        data[id].setdefault("dispositivos", []).append({"timestamp": now, "user_agent": user_agent})
        save_db(data)
        return redirect(data[id]['url'])
    return "QR no encontrado", 404

# Descarga
@app.route('/download/<id>')
@auth.login_required
def download(id):
    format = request.args.get('format', 'png').lower()
    path = f"{QR_FOLDER}/{id}.png"

    if not os.path.exists(path):
        return "QR no encontrado", 404

    img = Image.open(path)
    name = load_db().get(id, {}).get("name", f"qr_{id}").replace(" ", "_")

    if format == "png":
        return send_file(path, as_attachment=True, download_name=f"{name}.png", mimetype='image/png')
    elif format == "jpg":
        buffer = BytesIO()
        img.convert("RGB").save(buffer, format="JPEG")
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"{name}.jpg", mimetype='image/jpeg')
    elif format == "pdf":
        buffer = BytesIO()
        img.convert("RGB").save(buffer, format="PDF")
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"{name}.pdf", mimetype='application/pdf')
    return "Formato no soportado", 400

# Iniciar servidor
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

