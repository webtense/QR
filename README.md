# Gestor de Códigos QR

Aplicación sencilla para crear, editar y administrar códigos QR dentro de una organización. Incluye una interfaz gráfica protegida por contraseña, un modo de consola y la posibilidad de instalarse como servicio.

## Características principales
- Inicio de sesión obligatorio en la interfaz gráfica (usuario `Admin`, contraseña `BTR6969`).
- Dos tipos de códigos: **normal** (URL o texto) y **WiFi** (nombre de red y contraseña).
- Personalización de colores, texto opcional y formatos de salida **PNG** o **SVG** con vista previa.
- Edición y eliminación de códigos ya creados; todos los datos se guardan en `qr_data.json`.
- Modo consola sin contraseña para administraciones rápidas.
- Opción de instalar un servicio `systemd` que lanza la interfaz al arrancar el sistema.

## Requisitos
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

### Interfaz gráfica
1. Ejecuta la aplicación:
   ```bash
   python3 qr_manager.py
   ```
2. Introduce las credenciales solicitadas:
   - Usuario: `Admin`
   - Contraseña: `BTR6969`
3. Selecciona el tipo de QR:
   - **Normal**: escribe la URL o texto interno.
   - **WiFi**: indica el nombre de la red (SSID) y su contraseña.
4. Personaliza colores, agrega texto opcional y elige formato **PNG** o **SVG**.
5. Haz clic en **Guardar** para generar el código. Se mostrará una vista previa y el archivo se guardará en el directorio actual.
6. Para editar o borrar un código existente, selecciónalo de la lista y usa los botones correspondientes.

### Modo consola (sin contraseña)
```bash
python3 qr_manager.py --cli
```
Permite realizar las mismas operaciones desde el terminal sin solicitar inicio de sesión.

### Instalar como servicio (opcional)
```bash
python3 qr_manager.py --install-service
```
Requiere `sudo`. Crea un servicio `systemd` llamado `qr_manager` que abre la interfaz al iniciar el sistema.

### Archivos generados
- `qr_data.json`: base de datos sencilla con información de los códigos creados.
- Archivos PNG o SVG con los códigos QR en el directorio donde ejecutes la aplicación.

## Actualizar el programa
Cuando haya una nueva versión, navega al directorio del proyecto y ejecuta:
```bash
git pull
```

## Problemas comunes
- **Error: no se encuentra el paquete `qrcode` o `Pillow`**: asegúrate de haber ejecutado `pip install -r requirements.txt`. Si estás detrás de un proxy, configura las variables de entorno `http_proxy` y `https_proxy`.
- **Permiso denegado al instalar el servicio**: ejecuta el comando con `sudo`.
- **No aparece la ventana gráfica**: asegúrate de tener un entorno de escritorio disponible o usa el modo consola.

## Desinstalar el servicio (opcional)
Si ya no deseas que se ejecute al inicio:
```bash
sudo systemctl disable qr_manager.service
sudo rm /etc/systemd/system/qr_manager.service
```

¡Listo! Con estos pasos cualquier persona, incluso sin experiencia previa, puede gestionar sus códigos QR.

