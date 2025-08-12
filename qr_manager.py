import json
import os
import subprocess
import logging
from functools import wraps
from typing import Dict, Any

from flask import Flask, render_template, request, redirect, url_for, session, flash
import qrcode
from qrcode.image.svg import SvgImage
from PIL import Image, ImageDraw, ImageFont

DATA_FILE = "qr_data.json"
LOG_FILE = "qr_manager.log"
QR_DIR = os.path.join("static", "qrs")
os.makedirs(QR_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s %(message)s")

app = Flask(__name__)
app.secret_key = "super-secret"  # cambie esta clave en producción


def load_data() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def generate_qr(name: str, info: Dict[str, Any]) -> str:
    if info["type"] == "url":
        qr_data = info.get("url", "")
    else:
        qr_data = f"WIFI:T:{info.get('encryption','WPA')};S:{info.get('ssid','')};P:{info.get('password','')};;"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(qr_data)
    qr.make(fit=True)
    fmt = info.get("format", "png").lower()
    color = info.get("color", "black")
    background = info.get("background", "white")
    filename = f"{name}.{fmt if fmt == 'svg' else 'png'}"
    filepath = os.path.join(QR_DIR, filename)
    if fmt == "svg":
        img = qr.make_image(image_factory=SvgImage, fill_color=color, back_color=background)
        img.save(filepath)
    else:
        img = qr.make_image(fill_color=color, back_color=background)
        img.save(filepath)
        text = info.get("text")
        if text:
            try:
                img_with_text = Image.open(filepath)
                draw = ImageDraw.Draw(img_with_text)
                font = ImageFont.load_default()
                w, h = img_with_text.size
                draw.text((10, h - 10), text, fill=color, font=font, anchor="ld")
                img_with_text.save(filepath)
            except Exception:
                pass
    logging.info("Generado %s", filename)
    return filename


def install_service() -> None:
    script = os.path.abspath(__file__)
    python = os.environ.get("PYTHON", "python3")
    service = f"""[Unit]
Description=QR Manager Web
After=network.target

[Service]
ExecStart={python} {script}
Restart=always
User={os.environ.get('USER', 'root')}

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/qr_manager.service"
    tmp_file = "qr_manager.service"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(service)
    try:
        subprocess.run(["sudo", "cp", tmp_file, service_path], check=True)
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "--now", "qr_manager"], check=True)
        logging.info("Servicio instalado")
    except Exception as e:  # pragma: no cover - depende del sistema
        logging.error("No se pudo instalar el servicio: %s", e)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        if request.form.get("username") == "Admin" and request.form.get("password") == "BTR6969":
            session["user"] = "Admin"
            return redirect(url_for("dashboard"))
        flash("Credenciales incorrectas")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    data = load_data()
    return render_template("dashboard.html", data=data)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create_qr():
    if request.method == "POST":
        name = request.form.get("name")
        info = {
            "type": request.form.get("type", "url"),
            "url": request.form.get("data"),
            "ssid": request.form.get("data"),
            "password": request.form.get("password"),
            "text": request.form.get("text"),
            "color": request.form.get("color"),
            "background": request.form.get("background"),
            "format": request.form.get("format", "png"),
        }
        generate_qr(name, info)
        data = load_data()
        data[name] = info
        save_data(data)
        flash("QR guardado")
        return redirect(url_for("dashboard"))
    info = {"type": "url"}
    return render_template("form.html", name="", info=info)


@app.route("/edit/<name>", methods=["GET", "POST"])
@login_required
def edit_qr(name):
    data = load_data()
    info = data.get(name)
    if not info:
        flash("QR no encontrado")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        info.update({
            "type": request.form.get("type", "url"),
            "url": request.form.get("data"),
            "ssid": request.form.get("data"),
            "password": request.form.get("password"),
            "text": request.form.get("text"),
            "color": request.form.get("color"),
            "background": request.form.get("background"),
            "format": request.form.get("format", "png"),
        })
        generate_qr(name, info)
        save_data(data)
        flash("QR actualizado")
        return redirect(url_for("dashboard"))
    return render_template("form.html", name=name, info=info)


@app.route("/delete/<name>")
@login_required
def delete_qr(name):
    data = load_data()
    info = data.pop(name, None)
    if info:
        save_data(data)
        fname = f"{name}.{info.get('format', 'png')}" if info.get('format') == 'svg' else f"{name}.png"
        try:
            os.remove(os.path.join(QR_DIR, fname))
        except FileNotFoundError:
            pass
        flash("QR eliminado")
    return redirect(url_for("dashboard"))


@app.route("/tools")
@login_required
def tools():
    log_content = ""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_content = f.read()
    return render_template("tools.html", log=log_content)


@app.route("/tools/install", methods=["POST"])
@login_required
def install_service_route():
    install_service()
    flash("Solicitud de instalación enviada")
    return redirect(url_for("tools"))


@app.route("/tools/status")
@login_required
def service_status():
    try:
        output = subprocess.check_output(["systemctl", "status", "qr_manager"], text=True)
    except Exception as e:  # pragma: no cover - depende del sistema
        output = str(e)
    return render_template("status.html", status=output)


if __name__ == "__main__":
    app.run(debug=True)
