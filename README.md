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
1. Ejecuta `python3 qr_manager.py`.
2. Ingresa las credenciales:
   - Usuario: `Admin`
   - Contraseña: `BTR6969`
3. Utiliza el menú para crear, listar, editar o eliminar códigos QR.
   - Puedes elegir entre un QR normal (URL interna) o un QR con contraseña de WiFi.
   - Es posible añadir texto, elegir formato (PNG o SVG) y colores.
   - Los archivos se guardan en el directorio actual.

La información de los QR se guarda en `qr_data.json` para futuras ediciones.
