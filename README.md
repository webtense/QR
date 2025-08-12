# QR
Gestor simple de códigos QR para una organización.

## Guía rápida para principiantes

### 1. Instalar Git (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git
```

### 2. Clonar el repositorio
```bash
git clone https://github.com/USER/QR.git
cd QR
```
Para actualizar en el futuro:
```bash
git pull
```

### 3. Instalar Python y pip
```bash
sudo apt install python3 python3-pip
```

### 4. Instalar dependencias del proyecto
```bash
pip install -r requirements.txt
```

## Uso
### Interfaz gráfica
1. Ejecuta `python3 qr_manager.py`.
2. Ingresa las credenciales:
   - Usuario: `Admin`
   - Contraseña: `BTR6969`
3. Desde la interfaz puedes crear, editar o eliminar códigos QR.
   - Elige entre un QR normal (URL interna) o un QR con contraseña de WiFi.
   - Añade texto opcional, colores personalizados y formato de salida (PNG o SVG).
   - Se muestra una previsualización del QR generado.

### Consola (sin contraseña)
```bash
python3 qr_manager.py --cli
```
El modo consola permite las mismas operaciones sin solicitar credenciales.

### Instalar como servicio
```bash
python3 qr_manager.py --install-service
```
Requiere permisos de `sudo` y crea un servicio `systemd` que ejecuta la interfaz gráfica al iniciar.

Los archivos generados se guardan en el directorio actual y los datos quedan registrados en `qr_data.json` para futuras ediciones.
