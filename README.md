# SCBMAA – Sistema de Clasificación y Búsqueda de Mercancías y Aranceles

Sistema web desarrollado en Django para la consulta y administración básica de códigos arancelarios.

🔗 **Demo:** https://scbmaa.onrender.com  
📦 **Backend:** Django  
🗄️ **BD:** SQLite3  

---

## 🚀 Características
- Búsqueda por código arancelario y descripción
- Visualización de la tabla arancelaria
- Historial de consultas
- Administración de partidas y subpartidas

## 📦 Tecnologías
- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Django 5.2.3, Python 3.12
- **BD:** SQLite3

---

## 🧩 Instalación

```bash
# Ir al directorio donde se guardará el proyecto
cd C:\Usuarios

# Clonar el repositorio
git clone -b main https://github.com/Bot-350/SCBMAA.git

# Entrar al proyecto
cd SCBMAA

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear superusuario
python manage.py createsuperuser

# Ejecutar el servidor
python manage.py runserver
Abrir en el navegador: http://127.0.0.1:8000/

📂 Estructura del Proyecto
SCBMAA/
├── aranceles/           # App principal del sistema arancelario
├── usuarios/            # Gestión de usuarios y autenticación
├── inicial/             # Página de inicio
├── SCMAA/               # Configuración del proyecto Django
├── templates/           # Plantillas HTML
├── staticfiles/         # Archivos estáticos
├── manage.py            # Utilidad de línea de comandos Django
└── requirements.txt     # Dependencias del proyecto
📝 Licencia
Proyecto privado — Prohibida su distribución sin autorización.



