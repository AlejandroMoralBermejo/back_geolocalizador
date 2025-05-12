# back_geolocalizador

# API de Gestión de Usuarios, Dispositivos y Registros - FastAPI

Este proyecto es una API RESTful desarrollada con **FastAPI** y **SQLAlchemy** para la gestión de dispositivos de geolocalización. Soporta autenticación JWT, protección CORS y operaciones CRUD completas para las entidades mencionadas.

## 🚀 Características

- Autenticación segura con JWT
- Hash de contraseñas con bcrypt
- Operaciones CRUD para usuarios, dispositivos y registros
- Formateo automático de coordenadas GNSS
- Control de acceso a través de `OAuth2PasswordBearer`
- Middleware CORS habilitado
- Soporte para despliegue local o mediante Docker

## 📦 Instalación

### Opción 1: Ejecutar localmente

1. Clona el repositorio:
   git clone https://github.com/AlejandroMoralBermejo/back_geolocalizador.git
   cd back_geolocalizador.git

2. Crea un entorno virtual:
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate

3. Instala las dependencias:
   pip install -r requirements.txt

4. Ejecuta el servidor:
   uvicorn main:app --reload

   La API estará disponible en: http://127.0.0.1:8000

### Opción 2: Ejecutar con Docker Compose 🐳

1. Asegurate tener instalado Docker y Docker Compose:
   docker build -t fastapi-api .

2. Ejecuta:
   docker-compose up --build

   La API estará disponible en: http://localhost:8000

## 🔐 Autenticación

- Endpoint de login: POST /token
- Envía un JSON con `username`, `email` y `password` para obtener un token de acceso. *Por defecto te genera al inicio un usuario con username root, contraseña root y email root@root.root que puedes cambiar*
- Usa el token como Bearer en el header de autorización.
  

## 📚 Endpoints

Puedes probar todos los endpoints en la documentación automática que genera FastAPI:

- Swagger UI: http://localhost:8000/docs

*Los roles creados de manear automatica al generar la base de datos son:
  {
        "id": 1,
        "nombre": "root"
    },
    {
        "id": 2,
        "nombre": "admin" 
    },
    {
        "id": 3,
        "nombre": "user"
    },
    {
        "id": 4,
        "nombre": "premium"
    }
*

## 🗃️ Estructura del Proyecto

- `main.py` — Punto de entrada de la aplicación.
- `models.py` — Modelos de base de datos (Usuario, Dispositivo, Registro y Roles).
- `database.py` — Configuración de SQLAlchemy.

## 🧪 Requisitos

- Python 3.10 o superior
- Pip
- Docker (opcional)


## 📝 Licencia

MIT. Libre uso y modificación con atribución.
