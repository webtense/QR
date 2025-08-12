import json
import os
from getpass import getpass
from typing import Dict, Any

import qrcode
from qrcode.image.svg import SvgImage

DATA_FILE = "qr_data.json"


def load_data() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def generate_qr_entry(name: str, info: Dict[str, Any]) -> None:
    qr_data = ""
    if info["type"] == "url":
        qr_data = info["url"]
    elif info["type"] == "wifi":
        qr_data = f"WIFI:T:{info.get('encryption','WPA')};S:{info['ssid']};P:{info['password']};;"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(qr_data)
    qr.make(fit=True)
    fmt = info.get("format", "png").lower()
    color = info.get("color", "black")
    background = info.get("background", "white")
    if fmt == "svg":
        img = qr.make_image(image_factory=SvgImage, fill_color=color, back_color=background)
        filename = f"{name}.svg"
        img.save(filename)
    else:
        img = qr.make_image(fill_color=color, back_color=background)
        filename = f"{name}.png"
        img.save(filename)
        text = info.get("text")
        if text:
            try:
                from PIL import Image, ImageDraw, ImageFont
                img_with_text = Image.open(filename)
                draw = ImageDraw.Draw(img_with_text)
                font = ImageFont.load_default()
                w, h = img_with_text.size
                draw.text((10, h - 10), text, fill=color, font=font, anchor="ld")
                img_with_text.save(filename)
            except Exception:
                pass
    print(f"QR guardado en {filename}")


def create_qr(data: Dict[str, Any]) -> None:
    name = input("Nombre del QR: ")
    if name in data:
        print("El nombre ya existe")
        return
    qr_type = input("Tipo (url/wifi) [url]: ") or "url"
    info: Dict[str, Any] = {"type": qr_type}
    if qr_type == "wifi":
        info["ssid"] = input("Nombre de red (SSID): ")
        info["password"] = input("Contraseña WiFi: ")
        info["encryption"] = input("Encriptación (WPA/WEP/n) [WPA]: ") or "WPA"
    else:
        info["url"] = input("URL interna: ")
    info["text"] = input("Texto adicional (opcional): ") or None
    info["format"] = input("Formato (png/svg) [png]: ") or "png"
    info["color"] = input("Color principal [black]: ") or "black"
    info["background"] = input("Color de fondo [white]: ") or "white"
    data[name] = info
    save_data(data)
    generate_qr_entry(name, info)


def list_qrs(data: Dict[str, Any]) -> None:
    if not data:
        print("No hay QRs registrados")
        return
    for name, info in data.items():
        print(f"- {name}: {info['type']}")


def edit_qr(data: Dict[str, Any]) -> None:
    name = input("Nombre del QR a editar: ")
    if name not in data:
        print("QR no encontrado")
        return
    info = data[name]
    if info["type"] == "wifi":
        info["ssid"] = input(f"Nombre de red (SSID) [{info['ssid']}]: ") or info["ssid"]
        info["password"] = input(f"Contraseña WiFi [{info['password']}]: ") or info["password"]
        info["encryption"] = input(f"Encriptación [{info.get('encryption','WPA')}]: ") or info.get("encryption", "WPA")
    else:
        info["url"] = input(f"URL interna [{info['url']}]: ") or info["url"]
    info["text"] = input(f"Texto adicional [{info.get('text','') or ''}]: ") or info.get("text")
    info["format"] = input(f"Formato (png/svg) [{info.get('format','png')}]: ") or info.get("format", "png")
    info["color"] = input(f"Color principal [{info.get('color','black')}]: ") or info.get("color", "black")
    info["background"] = input(f"Color de fondo [{info.get('background','white')}]: ") or info.get("background", "white")
    data[name] = info
    save_data(data)
    generate_qr_entry(name, info)


def delete_qr(data: Dict[str, Any]) -> None:
    name = input("Nombre del QR a eliminar: ")
    if name in data:
        del data[name]
        save_data(data)
        print("QR eliminado")
    else:
        print("QR no encontrado")


def main() -> None:
    user = input("Usuario: ")
    pwd = getpass("Contraseña: ")
    if not (user == "Admin" and pwd == "BTR6969"):
        print("Credenciales incorrectas")
        return
    data = load_data()
    while True:
        print("\n--- Gestor de QR ---")
        print("1. Crear QR")
        print("2. Listar QRs")
        print("3. Editar QR")
        print("4. Eliminar QR")
        print("5. Salir")
        choice = input("Opción: ")
        if choice == "1":
            create_qr(data)
        elif choice == "2":
            list_qrs(data)
        elif choice == "3":
            edit_qr(data)
        elif choice == "4":
            delete_qr(data)
        elif choice == "5":
            break
        else:
            print("Opción no válida")


if __name__ == "__main__":
    main()
