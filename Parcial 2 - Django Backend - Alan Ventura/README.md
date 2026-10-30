# Taller: Endpoints en Django nativo

**Estudiante:** Alan Ventura
**Docente:** Jose Javier Torres Vanstrahlen
**Curso:** Desarrollo de aplicaciones Web I - 4E

---

## Tabla de contenido

1. [Introducción](#1-introducción)
2. [¿Qué es un endpoint?](#2-qué-es-un-endpoint)
3. [Verbos HTTP y su relación con CRUD](#3-verbos-http-y-su-relación-con-crud)
4. [Cómo funciona una vista basada en clase](#4-cómo-funciona-una-vista-basada-en-clase)
5. [Módulos, funciones y decoradores usados](#5-módulos-funciones-y-decoradores-usados)
6. [Aplicación en mi proyecto](#6-aplicación-en-mi-proyecto)
7. [Cómo ejecutar el proyecto](#7-cómo-ejecutar-el-proyecto)
8. [Cómo probar los endpoints](#8-cómo-probar-los-endpoints)
9. [Pruebas automáticas](#9-pruebas-automáticas)


---

## 1. Introducción

En este taller investigué cómo crear endpoints (rutas que devuelven datos, normalmente en JSON) usando solamente Django, sin instalar librerías externas como Django REST Framework. La idea es entender cómo funciona Django por dentro: cómo recibe una petición HTTP, cómo la distribuye según el verbo (GET, POST, PUT o DELETE) y cómo responde.

Para esto usé una **vista basada en clase (Class-Based View)** llamada `ProyectoView`, que hereda de `View` y tiene los métodos `get()`, `post()`, `put()` y `delete()`. La apliqué sobre el modelo `Proyecto` de mi proyecto de gestión de tareas.

## 2. ¿Qué es un endpoint?

Un endpoint es una URL a la que un cliente (el navegador, Postman, una app móvil, etc.) le hace una petición para obtener o modificar información. En este proyecto las URLs son `/api/proyectos/` y `/api/proyectos/<id>/`, y lo que pasa depende del verbo HTTP con el que se llamen.

## 3. Verbos HTTP y su relación con CRUD

CRUD son las cuatro operaciones básicas sobre los datos: Create, Read, Update y Delete. Cada una se asocia con un verbo HTTP:

| Verbo | Operación CRUD | Método en la vista | Caso de uso en el proyecto | Código de respuesta |
|-------|----------------|--------------------|----------------------------|---------------------|
| GET | Read (leer) | `get()` | Listar todos los proyectos o consultar uno por su id | 200 (o 404 si no existe) |
| POST | Create (crear) | `post()` | Registrar un proyecto nuevo con los datos enviados en el cuerpo | 201 (o 400 si los datos son inválidos) |
| PUT | Update (actualizar) | `put()` | Reemplazar los datos de un proyecto existente | 200 (o 400 / 404) |
| DELETE | Delete (eliminar) | `delete()` | Borrar un proyecto existente | 200 (o 404 si no existe) |

Notas que encontré en la investigación:

- **GET** es un método "seguro": solo consulta y no modifica datos.
- **GET, PUT y DELETE son idempotentes**: si se repite la misma petición varias veces, el resultado en el servidor es el mismo. **POST no lo es**, porque cada llamada crea un recurso nuevo.
- **PUT** reemplaza el recurso completo, por eso en mi vista hay que enviar todos los campos (`nombre`, `descripcion` y `fecha_inicio`). Para cambiar solo un campo existe el verbo PATCH, pero el taller pide únicamente los cuatro anteriores.
- Django solo llena `request.POST` con formularios enviados por POST. Para PUT y DELETE (y para JSON en general) hay que leer el cuerpo con `request.body` y convertirlo con `json.loads()`.

## 4. Cómo funciona una vista basada en clase

Cuando llega una petición, Django llama al método `dispatch()` de la clase `View`. Este método revisa el verbo HTTP (`request.method`) y ejecuta el método de la clase con ese mismo nombre en minúscula. Si la clase no tiene ese método, Django responde automáticamente con el error **405 Method Not Allowed**.

Por eso basta con definir `get()`, `post()`, `put()` y `delete()` y no hace falta escribir `if request.method == "POST"` dentro de la vista.

El flujo completo en mi proyecto es:

```
Petición HTTP  ->  config/urls.py  ->  gestion/urls.py  ->  ProyectoView.as_view()
                                                                    |
                                                          dispatch() elige el método
                                                      get() / post() / put() / delete()
                                                                    |
                                                  Modelo Proyecto (base de datos)  ->  JsonResponse
```

## 5. Módulos, funciones y decoradores usados

### 5.1 Módulos y clases

| Elemento | Descripción |
|----------|-------------|
| `django.views.View` | Clase base de las vistas basadas en clase. Redirige cada petición al método que corresponde al verbo HTTP. |
| `django.http.JsonResponse` | Clase que crea una respuesta HTTP con contenido JSON y el encabezado `Content-Type: application/json`. Recibe un diccionario y un `status` opcional. |
| `django.urls.path` | Función que define una ruta (URL) y la asocia con una vista. Permite capturar parámetros como `<int:pk>`. |
| `django.urls.include` | Permite incluir las URLs de una app dentro del `urls.py` principal del proyecto. |
| `django.db.models.Model` | Clase base para crear los modelos (tablas) de la base de datos, en este caso `Proyecto` y `Tarea`. |
| `json` (librería estándar de Python) | Se usa `json.loads()` para convertir el cuerpo de la petición (texto JSON) en un diccionario de Python. |
| `datetime.date` (librería estándar de Python) | Se usa `date.fromisoformat()` para validar que `fecha_inicio` venga en formato `AAAA-MM-DD`. |
| `django.test.TestCase` | Clase para escribir pruebas automáticas con una base de datos temporal. |

### 5.2 Funciones y métodos

| Elemento | Descripción |
|----------|-------------|
| `View.as_view()` | Convierte la clase en una función que Django puede usar en `urls.py`. |
| `View.dispatch()` | Método interno que decide qué método de la clase ejecutar según el verbo HTTP. |
| `request.body` | Contiene el cuerpo crudo de la petición (en bytes). Se usa para leer el JSON enviado en POST y PUT. |
| `request.method` | Texto con el verbo HTTP de la petición (`"GET"`, `"POST"`, etc.). |
| `Proyecto.objects.all()` | Devuelve todos los registros de la tabla. |
| `Proyecto.objects.filter(pk=...)` | Filtra registros por condición. Con `.first()` devuelve el primero o `None` si no existe. |
| `Proyecto.objects.create(...)` | Crea y guarda un registro nuevo en la base de datos. |
| `proyecto.save()` | Guarda en la base de datos los cambios hechos a un objeto existente. |
| `proyecto.delete()` | Elimina el registro de la base de datos. |
| `proyecto_a_dict()` | Función mía que convierte un `Proyecto` en un diccionario para poder enviarlo como JSON. |
| `leer_json()` | Función mía que lee el cuerpo de la petición y devuelve `None` si el JSON no es válido. |
| `validar_datos()` | Función mía que revisa los campos obligatorios y el formato de la fecha antes de guardar. |

### 5.3 Decoradores

| Elemento | Descripción |
|----------|-------------|
| `@csrf_exempt` | Del módulo `django.views.decorators.csrf`. Desactiva la verificación del token CSRF en una vista. Se necesita para poder probar POST, PUT y DELETE desde Postman o curl sin enviar el token. |
| `@method_decorator` | Del módulo `django.utils.decorators`. Permite aplicar un decorador pensado para funciones a una vista de clase. Se usa con `name="dispatch"` porque `dispatch()` es el método que recibe todas las peticiones. |
| `@require_http_methods` | Del módulo `django.views.decorators.http`. No lo usé porque en la vista de clase ya se controlan los verbos con los métodos, pero sirve para limitar los verbos permitidos en vistas basadas en funciones. |

> **Nota de seguridad:** usé `csrf_exempt` solo para efectos de práctica. En un proyecto real habría que dejar la protección CSRF activa o usar autenticación (por ejemplo, tokens o sesiones).

## 6. Aplicación en mi proyecto

### 6.1 Estructura

```
Parcial 2 - Django Backend - Alan Ventura/
├── config/
│   ├── settings.py
│   └── urls.py            <- incluye las rutas de la app con include()
├── gestion/
│   ├── models.py          <- modelos Proyecto y Tarea
│   ├── views.py           <- ProyectoView con get(), post(), put() y delete()
│   ├── urls.py            <- rutas proyectos/ y proyectos/<int:pk>/
│   ├── tests.py           <- 14 pruebas automáticas
│   └── admin.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

### 6.2 Archivos que modifiqué

| Archivo | Qué hice |
|---------|----------|
| `gestion/views.py` | Creé la clase `ProyectoView` con los cuatro métodos y las funciones auxiliares. |
| `gestion/urls.py` | Archivo nuevo (no existía) con las dos rutas del endpoint. |
| `config/urls.py` | Agregué `include('gestion.urls')` bajo el prefijo `api/`. |
| `gestion/tests.py` | Agregué las pruebas de cada verbo. |

### 6.3 Modelo usado

```python
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
```

### 6.4 Endpoints disponibles

| Método | URL | Qué hace | Cuerpo (JSON) |
|--------|-----|----------|---------------|
| GET | `/api/proyectos/` | Lista todos los proyectos | No lleva |
| POST | `/api/proyectos/` | Crea un proyecto | `nombre`, `descripcion`, `fecha_inicio` |
| GET | `/api/proyectos/<id>/` | Consulta un proyecto | No lleva |
| PUT | `/api/proyectos/<id>/` | Actualiza un proyecto | `nombre`, `descripcion`, `fecha_inicio` |
| DELETE | `/api/proyectos/<id>/` | Elimina un proyecto | No lleva |

La fecha se envía como texto en formato `AAAA-MM-DD` (por ejemplo `2026-10-29`).

### 6.5 Estructura de la vista

```python
@method_decorator(csrf_exempt, name="dispatch")
class ProyectoView(View):

    def get(self, request, pk=None):     # READ
        ...

    def post(self, request, pk=None):    # CREATE
        ...

    def put(self, request, pk=None):     # UPDATE
        ...

    def delete(self, request, pk=None):  # DELETE
        ...
```

Los métodos reciben `pk=None` porque la misma clase atiende las dos rutas: con `pk` se trabaja sobre un proyecto, y sin `pk` sobre la colección. Así, si alguien hace un PUT o un DELETE sin id, o un POST con id, la vista responde con un error claro en vez de fallar.

## 7. Cómo ejecutar el proyecto

En la terminal, dentro de la carpeta donde está `manage.py`:

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # en Windows
# source venv/bin/activate     # en Linux o Mac

# 2. Instalar las dependencias
pip install -r requirements.txt

# 3. Crear la base de datos
python manage.py migrate

# 4. (Opcional) crear un usuario para el panel de administración
python manage.py createsuperuser

# 5. Iniciar el servidor
python manage.py runserver
```

El servidor queda en `http://127.0.0.1:8000/`.

## 8. Cómo probar los endpoints

### Con Postman

1. Elegir el método (GET, POST, PUT o DELETE) y escribir la URL, por ejemplo `http://127.0.0.1:8000/api/proyectos/`.
2. Para POST y PUT, ir a **Body → raw → JSON** y escribir:

```json
{
  "nombre": "Proyecto 1",
  "descripcion": "Primer proyecto",
  "fecha_inicio": "2026-10-29"
}
```

3. Pulsar **Send** y revisar el código de estado y la respuesta.

### Con curl (Git Bash, Linux o Mac)

```bash
# POST - crear un proyecto
curl -X POST http://127.0.0.1:8000/api/proyectos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Proyecto 1", "descripcion": "Primer proyecto", "fecha_inicio": "2026-10-29"}'

# GET - listar todos
curl http://127.0.0.1:8000/api/proyectos/

# GET - consultar uno
curl http://127.0.0.1:8000/api/proyectos/1/

# PUT - actualizar
curl -X PUT http://127.0.0.1:8000/api/proyectos/1/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Proyecto 1 editado", "descripcion": "Descripcion nueva", "fecha_inicio": "2026-11-01"}'

# DELETE - eliminar
curl -X DELETE http://127.0.0.1:8000/api/proyectos/1/
```

### Con PowerShell (Windows)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/proyectos/ -Method Post `
  -ContentType "application/json" `
  -Body '{"nombre":"Proyecto 1","descripcion":"Primer proyecto","fecha_inicio":"2026-10-29"}'

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/proyectos/
```

### Ejemplos de respuesta

Al crear un proyecto (POST, código 201):

```json
{
  "id": 1,
  "nombre": "Proyecto 1",
  "descripcion": "Primer proyecto",
  "fecha_inicio": "2026-10-29"
}
```

Cuando hay un error (por ejemplo, un proyecto que no existe, código 404):

```json
{
  "error": "Proyecto no encontrado"
}
```

## 9. Pruebas automáticas

Escribí 14 pruebas en `gestion/tests.py` que verifican cada verbo, los casos de error (datos incompletos, fecha inválida, JSON mal formado, proyecto inexistente) y que un verbo no definido, como PATCH, responda 405. Para ejecutarlas:

```bash
python manage.py test
```

Resultado esperado:

```
Ran 14 tests in 0.0xs

OK
```
