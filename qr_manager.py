import argparse
import json
import os
import subprocess
from typing import Dict, Any

import qrcode
from qrcode.image.svg import SvgImage

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except Exception:  # pragma: no cover
    Image = ImageDraw = ImageFont = ImageTk = None

import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "qr_data.json"


def load_data() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def generate_qr_entry(name: str, info: Dict[str, Any]) -> str:
    qr_data = ""
    if info["type"] == "url":
        qr_data = info.get("url", "")
    elif info["type"] == "wifi":
        qr_data = f"WIFI:T:{info.get('encryption','WPA')};S:{info.get('ssid','')};P:{info.get('password','')};;"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(qr_data)
    qr.make(fit=True)
    fmt = info.get("format", "png").lower()
    color = info.get("color", "black")
    background = info.get("background", "white")
    filename = f"{name}.{fmt if fmt == 'svg' else 'png'}"
    if fmt == "svg":
        img = qr.make_image(image_factory=SvgImage, fill_color=color, back_color=background)
        img.save(filename)
    else:
        img = qr.make_image(fill_color=color, back_color=background)
        img.save(filename)
        text = info.get("text")
        if text and Image is not None:
            try:
                img_with_text = Image.open(filename)
                draw = ImageDraw.Draw(img_with_text)
                font = ImageFont.load_default()
                w, h = img_with_text.size
                draw.text((10, h - 10), text, fill=color, font=font, anchor="ld")
                img_with_text.save(filename)
            except Exception:
                pass
    return filename


def install_service() -> None:
    script = os.path.abspath(__file__)
    python = os.environ.get("PYTHON", "python3")
    service = f"""[Unit]
Description=QR Manager GUI
After=network.target

[Service]
ExecStart={python} {script}
Restart=always
User={os.environ.get('USER', 'root')}
Environment=DISPLAY=:0

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
        print("Servicio instalado y iniciado")
    except Exception as e:
        print("No se pudo instalar el servicio:", e)
        print("Puedes copiar manualmente el archivo qr_manager.service a /etc/systemd/system y habilitarlo")


# ---------------- CLI -----------------

def run_cli() -> None:
    data = load_data()
    while True:
        print("\n--- Gestor de QR (CLI) ---")
        print("1. Crear QR")
        print("2. Listar QRs")
        print("3. Editar QR")
        print("4. Eliminar QR")
        print("5. Salir")
        choice = input("Opción: ")
        if choice == "1":
            create_qr_cli(data)
        elif choice == "2":
            list_qrs_cli(data)
        elif choice == "3":
            edit_qr_cli(data)
        elif choice == "4":
            delete_qr_cli(data)
        elif choice == "5":
            break
        else:
            print("Opción no válida")


def create_qr_cli(data: Dict[str, Any]) -> None:
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


def list_qrs_cli(data: Dict[str, Any]) -> None:
    if not data:
        print("No hay QRs registrados")
        return
    for name, info in data.items():
        print(f"- {name}: {info['type']}")


def edit_qr_cli(data: Dict[str, Any]) -> None:
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


def delete_qr_cli(data: Dict[str, Any]) -> None:
    name = input("Nombre del QR a eliminar: ")
    if name in data:
        del data[name]
        save_data(data)
        print("QR eliminado")
    else:
        print("QR no encontrado")


# ---------------- GUI -----------------

class LoginWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Inicio de sesión")
        tk.Label(self, text="Usuario").grid(row=0, column=0, pady=5, padx=5)
        tk.Label(self, text="Contraseña").grid(row=1, column=0, pady=5, padx=5)
        self.user_entry = tk.Entry(self)
        self.pwd_entry = tk.Entry(self, show="*")
        self.user_entry.grid(row=0, column=1)
        self.pwd_entry.grid(row=1, column=1)
        tk.Button(self, text="Entrar", command=self.check_login).grid(row=2, column=0, columnspan=2, pady=5)

    def check_login(self) -> None:
        if self.user_entry.get() == "Admin" and self.pwd_entry.get() == "BTR6969":
            self.destroy()
            app = App()
            app.mainloop()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gestor de QR")
        self.data = load_data()
        self.current_image = None
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self) -> None:
        left = tk.Frame(self)
        left.pack(side=tk.LEFT, padx=10, pady=10)
        right = tk.Frame(self)
        right.pack(side=tk.RIGHT, padx=10, pady=10)

        self.listbox = tk.Listbox(left, width=25)
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        form = tk.Frame(left)
        form.pack(pady=10)
        tk.Label(form, text="Nombre").grid(row=0, column=0, sticky="e")
        tk.Label(form, text="Tipo").grid(row=1, column=0, sticky="e")
        tk.Label(form, text="URL").grid(row=2, column=0, sticky="e")
        tk.Label(form, text="SSID").grid(row=3, column=0, sticky="e")
        tk.Label(form, text="Password").grid(row=4, column=0, sticky="e")
        tk.Label(form, text="Texto").grid(row=5, column=0, sticky="e")
        tk.Label(form, text="Formato").grid(row=6, column=0, sticky="e")
        tk.Label(form, text="Color").grid(row=7, column=0, sticky="e")
        tk.Label(form, text="Fondo").grid(row=8, column=0, sticky="e")

        self.name_entry = tk.Entry(form)
        self.type_var = tk.StringVar(value="url")
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var, values=["url", "wifi"], state="readonly")
        self.url_entry = tk.Entry(form)
        self.ssid_entry = tk.Entry(form)
        self.pass_entry = tk.Entry(form)
        self.text_entry = tk.Entry(form)
        self.format_var = tk.StringVar(value="png")
        self.format_combo = ttk.Combobox(form, textvariable=self.format_var, values=["png", "svg"], state="readonly")
        self.color_entry = tk.Entry(form)
        self.bg_entry = tk.Entry(form)

        self.name_entry.grid(row=0, column=1)
        self.type_combo.grid(row=1, column=1)
        self.url_entry.grid(row=2, column=1)
        self.ssid_entry.grid(row=3, column=1)
        self.pass_entry.grid(row=4, column=1)
        self.text_entry.grid(row=5, column=1)
        self.format_combo.grid(row=6, column=1)
        self.color_entry.grid(row=7, column=1)
        self.bg_entry.grid(row=8, column=1)

        tk.Button(left, text="Guardar/Generar", command=self.save_qr).pack(pady=5)
        tk.Button(left, text="Eliminar", command=self.delete_qr).pack(pady=5)
        tk.Button(left, text="Instalar como servicio", command=install_service).pack(pady=5)

        self.image_label = tk.Label(right)
        self.image_label.pack()

    def refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for name in self.data.keys():
            self.listbox.insert(tk.END, name)

    def on_select(self, _event) -> None:
        if not self.listbox.curselection():
            return
        name = self.listbox.get(self.listbox.curselection()[0])
        info = self.data[name]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.type_var.set(info.get("type", "url"))
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, info.get("url", ""))
        self.ssid_entry.delete(0, tk.END)
        self.ssid_entry.insert(0, info.get("ssid", ""))
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.insert(0, info.get("password", ""))
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, info.get("text", ""))
        self.format_var.set(info.get("format", "png"))
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, info.get("color", "black"))
        self.bg_entry.delete(0, tk.END)
        self.bg_entry.insert(0, info.get("background", "white"))

    def save_qr(self) -> None:
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("Error", "Nombre requerido")
            return
        info: Dict[str, Any] = {
            "type": self.type_var.get(),
            "url": self.url_entry.get(),
            "ssid": self.ssid_entry.get(),
            "password": self.pass_entry.get(),
            "text": self.text_entry.get() or None,
            "format": self.format_var.get(),
            "color": self.color_entry.get() or "black",
            "background": self.bg_entry.get() or "white",
        }
        if info["type"] == "url" and not info["url"]:
            messagebox.showerror("Error", "URL requerida")
            return
        if info["type"] == "wifi" and not info["ssid"]:
            messagebox.showerror("Error", "SSID requerido")
            return
        self.data[name] = info
        save_data(self.data)
        filename = generate_qr_entry(name, info)
        messagebox.showinfo("Guardado", f"QR guardado en {filename}")
        self.refresh_list()
        if ImageTk is not None and os.path.exists(filename):
            img = Image.open(filename)
            img = img.resize((200, 200))
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image)

    def delete_qr(self) -> None:
        if not self.listbox.curselection():
            return
        name = self.listbox.get(self.listbox.curselection()[0])
        if name in self.data:
            del self.data[name]
            save_data(self.data)
            self.refresh_list()
            self.image_label.config(image="")


# ---------------- Main -----------------


def main() -> None:
    parser = argparse.ArgumentParser(description="QR Manager")
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo consola sin contraseña")
    parser.add_argument("--install-service", action="store_true", help="Instalar como servicio systemd")
    args = parser.parse_args()

    if args.install_service:
        install_service()
    elif args.cli:
        run_cli()
    else:
        login = LoginWindow()
        login.mainloop()


if __name__ == "__main__":
    main()
