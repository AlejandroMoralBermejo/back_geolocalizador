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
   ```bash
   git clone https://github.com/AlejandroMoralBermejo/back_geolocalizador.git
   cd back_geolocalizador
   ```

2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Genera el archivo .env:
   El archivo .env debe tener los siguientes parámetros
   SECRET_KEY=""
   ALGORITHM=""
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   PASSWORD_GMAIL=""
   MY_EMAIL=""
   BBDD_USER=""
   BBDD_PASSWORD=""

5. Asegurarte de la URL de la base de datos:
   En el caso de que lo ejecutes localmente sin Docker debes asegurarte de que 
   en el archivo database.py encuentres la siguiente url
   DATABASE_URL = f"postgresql://{usuarioDb}:{passwordDb}@localhost:5432/postgres"   

6. Ejecuta el servidor:
   ```bash
   uvicorn main:app --reload
   ```

   La API estará disponible en: http://127.0.0.1:8000

### Opción 2: Ejecutar con Docker Compose 🐳

1. Asegúrate de tener instalado Docker y Docker Compose:
   ```bash
   docker build -t fastapi-api .
   ```

2. También debes tener creado el .env con las variables:
   SECRET_KEY=""
   ALGORITHM=""
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   PASSWORD_GMAIL=""
   MY_EMAIL=""
   BBDD_USER=""
   BBDD_PASSWORD=""

3. Asegurarte de la URL de la base de datos:
   Debes asegurarte de que en el archivo database.py encuentres la siguiente url
   DATABASE_URL = f"postgresql://{usuarioDb}:{passwordDb}@:5432/postgres"

4. Ejecuta:
   ```bash
   docker-compose up --build
   ```

   La API estará disponible en: http://localhost:8000

## 🔐 Autenticación

- Endpoint de login: `POST /token`
- Envía un JSON con `username`, `email` y `password` para obtener un token de acceso.  
- Por defecto, se genera al iniciar un usuario con:
  - `username`: root  
  - `password`: root  
  - `email`: root@root.root  
  (Puedes cambiarlo si quieres)

- Usa el token como Bearer en el header de autorización.

## 📚 Endpoints

Puedes probar todos los endpoints en la documentación automática que genera FastAPI:

- Swagger UI: http://localhost:8000/docs

- Existe un par de endpoints especiales como lo son:

1. /api/v1.5/usuarios/cambiar_contrasena/{usuario_id}

   Este endpoint le mandará un correo al usuario del id con la url para cambiar la contraseña

2. /api/v1.5/usuarios/cambiar_contrasena/{usuario_id}/{token}

   Este endpoint se accede desde el correo mandado por el anterior ya que integra el token del correo

### 📌 Roles predefinidos

Los roles creados de manera automática al generar la base de datos son:

```json
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
```

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