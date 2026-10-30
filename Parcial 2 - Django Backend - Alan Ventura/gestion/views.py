# LIBRERIAS
import json
from datetime import date

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Proyecto


# FUNCIONES AUXILIARES
def proyecto_a_dict(proyecto):
    """Convierte un Proyecto en un diccionario para poder enviarlo como JSON."""
    return {
        "id": proyecto.id,
        "nombre": proyecto.nombre,
        "descripcion": proyecto.descripcion,
        "fecha_inicio": proyecto.fecha_inicio.isoformat(),
    }


def leer_json(request):
    """Lee el cuerpo de la peticion y lo convierte en diccionario.
    Devuelve None si el JSON no es valido o no es un objeto."""
    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        return None
    if not isinstance(datos, dict):
        return None
    return datos


def validar_datos(datos):
    """Revisa que vengan los campos obligatorios y que sean correctos.
    Devuelve una tupla (datos_limpios, mensaje_de_error)."""
    if datos is None:
        return None, "El cuerpo debe ser un JSON valido"

    nombre = datos.get("nombre")
    descripcion = datos.get("descripcion")
    fecha = datos.get("fecha_inicio")

    if not nombre or not descripcion or not fecha:
        return None, "Los campos 'nombre', 'descripcion' y 'fecha_inicio' son obligatorios"

    if not isinstance(nombre, str) or not isinstance(descripcion, str):
        return None, "'nombre' y 'descripcion' deben ser texto"

    if len(nombre) > 100:
        return None, "'nombre' no puede tener mas de 100 caracteres"

    try:
        fecha_inicio = date.fromisoformat(fecha)
    except (ValueError, TypeError):
        return None, "'fecha_inicio' debe tener el formato AAAA-MM-DD"

    return {
        "nombre": nombre,
        "descripcion": descripcion,
        "fecha_inicio": fecha_inicio,
    }, None


# VISTA
# csrf_exempt se aplica sobre dispatch() porque en una vista de clase no se
# puede decorar directamente get/post/put/delete: dispatch() es el metodo que
# recibe todas las peticiones y luego llama al que corresponde.
# NOTA: se desactiva CSRF solo para poder probar con Postman o curl en el taller.
@method_decorator(csrf_exempt, name="dispatch")
class ProyectoView(View):

    # GET -> READ (leer)
    def get(self, request, pk=None):
        # Con pk devolvemos un solo proyecto; sin pk, la lista completa
        if pk is not None:
            proyecto = Proyecto.objects.filter(pk=pk).first()
            if proyecto is None:
                return JsonResponse({"error": "Proyecto no encontrado"}, status=404)
            return JsonResponse(proyecto_a_dict(proyecto))

        proyectos = [proyecto_a_dict(p) for p in Proyecto.objects.all()]
        return JsonResponse({"proyectos": proyectos})

    # POST -> CREATE (crear)
    def post(self, request, pk=None):
        if pk is not None:
            return JsonResponse(
                {"error": "Para crear un proyecto usa POST en /api/proyectos/"},
                status=405,
            )

        datos, error = validar_datos(leer_json(request))
        if error:
            return JsonResponse({"error": error}, status=400)

        proyecto = Proyecto.objects.create(**datos)
        return JsonResponse(proyecto_a_dict(proyecto), status=201)

    # PUT -> UPDATE (actualizar)
    def put(self, request, pk=None):
        if pk is None:
            return JsonResponse({"error": "Falta el id del proyecto en la URL"}, status=400)

        proyecto = Proyecto.objects.filter(pk=pk).first()
        if proyecto is None:
            return JsonResponse({"error": "Proyecto no encontrado"}, status=404)

        datos, error = validar_datos(leer_json(request))
        if error:
            return JsonResponse({"error": error}, status=400)

        proyecto.nombre = datos["nombre"]
        proyecto.descripcion = datos["descripcion"]
        proyecto.fecha_inicio = datos["fecha_inicio"]
        proyecto.save()
        return JsonResponse(proyecto_a_dict(proyecto))

    # DELETE -> DELETE (eliminar)
    def delete(self, request, pk=None):
        if pk is None:
            return JsonResponse({"error": "Falta el id del proyecto en la URL"}, status=400)

        proyecto = Proyecto.objects.filter(pk=pk).first()
        if proyecto is None:
            return JsonResponse({"error": "Proyecto no encontrado"}, status=404)

        proyecto.delete()
        return JsonResponse({"mensaje": "Proyecto eliminado correctamente"})
