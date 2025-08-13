# regenerar_qrs.py
import os
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont

# Rutas
DATA_FILE = 'db.json'
QR_FOLDER = 'static/qrs'
UPLOAD_FOLDER = 'static/uploads'
FONT_PATH = 'static/fonts/Lobster-Regular.ttf'
DOMAIN = 'https://qr.boitaullresort.com/qr'

# Ajusta el tamaño de fuente automáticamente
def ajustar_fuente(texto, max_ancho, font_path, tamaño_inicial=40):
    tamaño = tamaño_inicial
    while tamaño > 10:
        font = ImageFont.truetype(font_path, tamaño)
        w = font.getbbox(texto)[2]
        if w <= max_ancho:
            return font
        tamaño -= 2
    return ImageFont.truetype(font_path, 10)

# Carga la base de datos
if not os.path.exists(DATA_FILE):
    print("❌ No se encuentra db.json")
    exit()

with open(DATA_FILE) as f:
    data = json.load(f)

# Crea la carpeta si no existe
os.makedirs(QR_FOLDER, exist_ok=True)

print("🔁 Regenerando todos los códigos QR...")

for id, info in data.items():
    url = f"{DOMAIN}/{id}"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_size = img.size[0]

    # Logo si existe
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

    # Texto en el centro
    if info.get("text_center"):
        font_center = ajustar_fuente(info["text_center"], qr_size - 40, FONT_PATH)
        bbox = font_center.getbbox(info["text_center"])
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((qr_size - w) / 2, (qr_size - h) / 2), info["text_center"], font=font_center, fill="black")

    # Texto inferior
    if info.get("text_bottom"):
        new_img = Image.new("RGB", (img.size[0], img.size[1] + 60), "white")
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        font_bottom = ImageFont.truetype(FONT_PATH, 40)
        bbox = font_bottom.getbbox(info["text_bottom"])
        w = bbox[2] - bbox[0]
        draw.text(((new_img.size[0] - w) / 2, img.size[1] + 5), info["text_bottom"], font=font_bottom, fill="black")
        img = new_img

    output_path = os.path.join(QR_FOLDER, f"{id}.png")
    img.save(output_path)
    print(f"[{id}] ✅ QR actualizado: {output_path}")

print("✅ Todos los QR han sido regenerados con el dominio qr.boitaullresort.com.")
