# QR
Gestor simple de códigos QR para una organización.

## Requisitos
- Python 3
- Instalación de dependencias:
  ```bash
  pip install -r requirements.txt
  ```

## Uso
1. Ejecuta `python qr_manager.py`.
2. Ingresa las credenciales:
   - Usuario: `Admin`
   - Contraseña: `BTR6969`
3. Utiliza el menú para crear, listar, editar o eliminar códigos QR.
   - Puedes elegir entre QR normal (URL interna) o QR para contraseña de WiFi.
   - Es posible añadir texto, elegir formato (PNG o SVG) y colores.
   - Los archivos se guardan en el directorio actual.

La información de los QR se almacena en `qr_data.json` para futuras ediciones.
