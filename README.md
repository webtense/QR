# Gestor de Códigos QR Web

Aplicación web para crear, editar y administrar códigos QR dentro de una organización. Todo se maneja desde el navegador y está protegido por inicio de sesión.

## Características
- Inicio de sesión obligatorio (usuario `Admin`, contraseña `BTR6969`).
- Dos tipos de códigos: **normal** (URL o texto) y **WiFi** (SSID y contraseña).
- Personalización de colores, texto opcional y formatos **PNG** o **SVG**.
- Menú **Herramientas** para ver el registro, instalar la aplicación como servicio `systemd` y consultar su estado.
- Los códigos y sus datos se guardan en `qr_data.json` y las imágenes en `static/qrs/`.

## Requisitos previos
- Ordenador con Ubuntu o Debian y acceso a Internet.
- Terminal con permisos de administrador (`sudo`).
- [Git](https://git-scm.com/), [Python 3](https://www.python.org/) y `pip`.

## Instalación paso a paso
1. **Instalar Git**
   ```bash
   sudo apt update
   sudo apt install git
   ```
2. **Clonar este repositorio**
   ```bash
   git clone https://github.com/USER/QR.git
   cd QR
   ```
   Para actualizar más tarde utiliza:
   ```bash
   git pull
   ```
3. **Instalar Python y pip (si no están)**
   ```bash
   sudo apt install python3 python3-pip
   ```
4. **Instalar dependencias del proyecto**
   ```bash
   pip install -r requirements.txt
   ```
   Si recibes un error de permisos añade `--user` o ejecuta el comando con `sudo`.

## Uso de la aplicación
1. Ejecuta el servidor:
   ```bash
   python3 qr_manager.py
   ```
2. Abre el navegador en `http://localhost:5000`.
3. Introduce las credenciales solicitadas:
   - Usuario: `Admin`
   - Contraseña: `BTR6969`
4. Desde el panel principal puedes:
   - Crear un nuevo código QR (normal o WiFi).
   - Editar o eliminar códigos existentes.
   - Acceder al menú **Herramientas**.
5. En **Herramientas** puedes:
   - Ver el contenido del archivo de log `qr_manager.log`.
   - Instalar la aplicación como servicio `systemd` (requiere `sudo`).
   - Consultar el estado del servicio `qr_manager`.

## Archivos generados
- `qr_data.json`: base de datos con la información de los códigos creados.
- `static/qrs/`: carpeta con las imágenes PNG o SVG generadas.
- `qr_manager.log`: registro de eventos de la aplicación.

## Actualizar el programa
Cuando haya una nueva versión, navega al directorio del proyecto y ejecuta:
```bash
git pull
```

## Problemas comunes
- **Faltan dependencias**: asegúrate de haber ejecutado `pip install -r requirements.txt`.
- **Permiso denegado al instalar el servicio**: ejecuta la acción con `sudo`.
- **No puedo acceder a la web**: verifica que el servidor esté en ejecución y que no haya un firewall bloqueando el puerto 5000.

## Desinstalar el servicio (opcional)
Si ya no deseas que se ejecute al inicio:
```bash
sudo systemctl disable qr_manager.service
sudo rm /etc/systemd/system/qr_manager.service
```

¡Listo! Con estos pasos cualquier persona, incluso sin experiencia previa, puede gestionar sus códigos QR desde una interfaz web.
