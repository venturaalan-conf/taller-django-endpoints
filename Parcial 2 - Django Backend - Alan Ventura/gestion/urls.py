# LIBRERIAS
from django.urls import path

from .views import ProyectoView

# RUTAS DE LA APP
# as_view() convierte la clase en una funcion que Django puede usar como vista
urlpatterns = [
    # GET (lista) y POST (crear)
    path("proyectos/", ProyectoView.as_view(), name="proyectos"),
    # GET (uno), PUT (actualizar) y DELETE (eliminar)
    path("proyectos/<int:pk>/", ProyectoView.as_view(), name="proyecto-detalle"),
]
