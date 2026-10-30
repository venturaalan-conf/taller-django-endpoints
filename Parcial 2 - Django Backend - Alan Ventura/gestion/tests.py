import json

from django.test import TestCase

from .models import Proyecto


class ProyectoViewTests(TestCase):

    def setUp(self):
        # Proyecto de prueba que se crea antes de cada test
        self.proyecto = Proyecto.objects.create(
            nombre="Proyecto inicial",
            descripcion="Descripcion inicial",
            fecha_inicio="2026-10-01",
        )
        self.datos_validos = {
            "nombre": "Proyecto nuevo",
            "descripcion": "Descripcion nueva",
            "fecha_inicio": "2026-11-15",
        }

    def enviar(self, metodo, url, datos=None):
        """Ayuda para enviar peticiones con JSON usando el cliente de pruebas."""
        return getattr(self.client, metodo)(
            url,
            data=json.dumps(datos) if datos is not None else None,
            content_type="application/json",
        )

    # GET
    def test_get_lista_proyectos(self):
        respuesta = self.client.get("/api/proyectos/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()["proyectos"]), 1)

    def test_get_un_proyecto(self):
        respuesta = self.client.get(f"/api/proyectos/{self.proyecto.id}/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["nombre"], "Proyecto inicial")

    def test_get_proyecto_inexistente(self):
        respuesta = self.client.get("/api/proyectos/999/")
        self.assertEqual(respuesta.status_code, 404)

    # POST
    def test_post_crea_proyecto(self):
        respuesta = self.enviar("post", "/api/proyectos/", self.datos_validos)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Proyecto.objects.count(), 2)

    def test_post_sin_nombre(self):
        datos = dict(self.datos_validos)
        del datos["nombre"]
        respuesta = self.enviar("post", "/api/proyectos/", datos)
        self.assertEqual(respuesta.status_code, 400)

    def test_post_fecha_invalida(self):
        datos = dict(self.datos_validos, fecha_inicio="15/11/2026")
        respuesta = self.enviar("post", "/api/proyectos/", datos)
        self.assertEqual(respuesta.status_code, 400)

    def test_post_json_invalido(self):
        respuesta = self.client.post(
            "/api/proyectos/", data="esto no es json", content_type="application/json"
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_post_sobre_un_proyecto_no_permitido(self):
        respuesta = self.enviar("post", f"/api/proyectos/{self.proyecto.id}/", self.datos_validos)
        self.assertEqual(respuesta.status_code, 405)

    # PUT
    def test_put_actualiza_proyecto(self):
        respuesta = self.enviar("put", f"/api/proyectos/{self.proyecto.id}/", self.datos_validos)
        self.assertEqual(respuesta.status_code, 200)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.nombre, "Proyecto nuevo")

    def test_put_proyecto_inexistente(self):
        respuesta = self.enviar("put", "/api/proyectos/999/", self.datos_validos)
        self.assertEqual(respuesta.status_code, 404)

    def test_put_sin_id(self):
        respuesta = self.enviar("put", "/api/proyectos/", self.datos_validos)
        self.assertEqual(respuesta.status_code, 400)

    # DELETE
    def test_delete_elimina_proyecto(self):
        respuesta = self.client.delete(f"/api/proyectos/{self.proyecto.id}/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Proyecto.objects.count(), 0)

    def test_delete_proyecto_inexistente(self):
        respuesta = self.client.delete("/api/proyectos/999/")
        self.assertEqual(respuesta.status_code, 404)

    # Verbo no definido en la vista
    def test_patch_no_permitido(self):
        respuesta = self.enviar("patch", f"/api/proyectos/{self.proyecto.id}/", {})
        self.assertEqual(respuesta.status_code, 405)
