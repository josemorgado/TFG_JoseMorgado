import os
import random
from datetime import date, timedelta

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from categoria.models import Categoria
from comentario.models import Comentario
from distrito.models import Distrito
from imagen.models import Imagen
from megusta.models import MeGusta
from perfil.models import Perfil
from quejas.models import Queja
from video.models import Video


class Command(BaseCommand):
    help = "Resetea y rellena la BD con datos masivos y heterogéneos para el TFG."

    def handle(self, *args, **kwargs):

        # ============================================================
        #  TRUNCATE TODAS LAS TABLAS (reinicia IDs)
        # ============================================================
        with connection.cursor() as cursor:
            for model in apps.get_models():
                table = model._meta.db_table
                cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;')
        self.stdout.write(self.style.SUCCESS("TRUNCATE OK."))

        # ============================================================
        #  CATEGORÍAS
        # ============================================================
        categorias = [
            {"nombre": "Tecnología", "descripcion": "Categoría relacionada con tecnología."},
            {"nombre": "Salud", "descripcion": "Categoría relacionada con salud y bienestar."},
            {"nombre": "Deportes", "descripcion": "Categoría relacionada con deportes y actividades físicas."},
            {"nombre": "Educación", "descripcion": "Categoría relacionada con educación y aprendizaje."},
            {"nombre": "Entretenimiento", "descripcion": "Categoría relacionada con entretenimiento y ocio."},
            {"nombre": "Igualdad", "descripcion": "Categoría relacionada con igualdad de oportunidades.", "activo": False},
            {"nombre": "Infraestructura", "descripcion": "Problemas de calles, alumbrado, obras."},
            {"nombre": "Transporte", "descripcion": "Autobuses, metro, tráfico, movilidad."},
            {"nombre": "Servicios Públicos", "descripcion": "Limpieza, basuras, ruido, etc."},
        ]
        for c in categorias:
            Categoria.objects.get_or_create(**c)
        self.stdout.write(self.style.SUCCESS("Categorías OK."))

        # ============================================================
        #  DISTRITOS
        # ============================================================
        distritos = [
            {"nombre": "Centro", "codigo": "CTR"},
            {"nombre": "Norte", "codigo": "NTE"},
            {"nombre": "Sur", "codigo": "SUR"},
            {"nombre": "Este", "codigo": "EST"},
            {"nombre": "Oeste", "codigo": "OES"},
            {"nombre": "Ribera", "codigo": "RBR"},
            {"nombre": "Puerta Real", "codigo": "PRL"},
        ]
        for d in distritos:
            Distrito.objects.get_or_create(**d)
        self.stdout.write(self.style.SUCCESS("Distritos OK."))

        # ============================================================
        #  USUARIOS (1 admin + 60 extra)
        # ============================================================
        usuarios = [
            {
                "username": "josem",
                "email": "jose@test.com",
                "password": "1234",
                "first_name": "José M",
                "last_name": "Morgado",
                "is_superuser": True,
                "is_staff": True,
                "perfil": {
                    "genero": "M",
                    "biografia": "Desarrollador del TFG.",
                    "moderator": True,
                    "telefono": "+34630974036",
                    "direccion": "Calle Fernando de Rojas",
                    "fecha_nacimiento": date(2003, 11, 20),
                },
            }
        ]
        for i in range(1, 61):
            usuarios.append(
                {
                    "username": f"user{i}",
                    "email": f"user{i}@test.com",
                    "password": "1234",
                    "first_name": f"Usuario{i}",
                    "last_name": "Demo",
                    "perfil": {
                        "genero": random.choice(["M", "F"]),
                        "biografia": f"Biografía del usuario {i}.",
                        "moderator": random.choice([False, False, False, True]),
                        "telefono": f"+34600{random.randint(100000, 999999)}",
                        "direccion": f"Calle Ejemplo {i}",
                        "fecha_nacimiento": date(1985 + (i % 20), (i % 12) + 1, (i % 27) + 1),
                    },
                }
            )

        for data in usuarios:
            perfil_data = data.pop("perfil")
            pwd = data.pop("password")
            username = data["username"]

            user, created = User.objects.get_or_create(username=username, defaults=data)
            if created:
                user.set_password(pwd)
                user.save()
            Perfil.objects.update_or_create(user=user, defaults=perfil_data)

        usuarios_obj = list(User.objects.all())
        self.stdout.write(self.style.SUCCESS(f"Usuarios OK ({len(usuarios_obj)})."))

        # ============================================================
        #  200 QUEJAS (10 base + 190 auto)
        # ============================================================
        categorias_obj = list(Categoria.objects.all())
        distritos_obj = list(Distrito.objects.all())

        quejas_payload = []
        base_quejas = [
            "Farolas rotas en avenida principal",
            "Autobuses llegan siempre tarde",
            "Basura acumulada en la plaza",
            "Ruidos nocturnos constantes",
            "Parque infantil en mal estado",
            "Semáforo averiado durante días",
            "Aceras resbaladizas",
            "Cortes de agua frecuentes",
            "Mal olor procedente de alcantarillado",
            "Árboles sin podar obstaculizan el paso",
        ]
        for titulo in base_quejas:
            quejas_payload.append(
                {
                    "titulo": titulo,
                    "descripcion": f"Descripción de: {titulo}",
                    "categoria": random.choice(categorias_obj),
                    "distrito": random.choice(distritos_obj),
                    "estado": random.choice(["PEN", "ENP", "REC", "RES"]),
                    "ubicacion": f"Ubicación específica de {titulo}",
                    "autor": random.choice(usuarios_obj),
                }
            )

        for i in range(1, 191):
            quejas_payload.append(
                {
                    "titulo": f"Queja generada #{i}",
                    "descripcion": f"Descripción automática de la queja #{i}",
                    "categoria": random.choice(categorias_obj),
                    "distrito": random.choice(distritos_obj),
                    "estado": random.choice(["PEN", "ENP", "REC", "RES"]),
                    "ubicacion": f"Zona aleatoria {i}",
                    "autor": random.choice(usuarios_obj),
                }
            )

        todas_quejas = []
        for payload in quejas_payload:
            q = Queja.objects.create(**payload)
            todas_quejas.append(q)

        self.stdout.write(self.style.SUCCESS(f"Quejas creadas: {len(todas_quejas)}"))

        # ============================================================
        #  ACTUALIZACIÓN DE FECHAS TRAS CREAR (TZ-AWARE)
        # ============================================================
        ahora = timezone.now()
        for q in todas_quejas:
            creacion = ahora - timedelta(
                days=random.randint(0, 150),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            actualizacion = creacion + timedelta(
                days=random.randint(0, 20),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            q.fecha_creacion = creacion
            q.fecha_actualizacion = actualizacion
            q.save(update_fields=["fecha_creacion", "fecha_actualizacion"])

        self.stdout.write(self.style.SUCCESS("Fechas de quejas actualizadas (aware)."))

        # ============================================================
        #  COMENTARIOS (heterogéneos con jerarquía)
        # ============================================================
        total_root = 120
        total_replies = 180
        total_deep = 80  # respuestas a respuestas
        comentarios_creados = []

        # 1) Comentarios raíz
        for i in range(total_root):
            c = Comentario.objects.create(
                queja=random.choice(todas_quejas),
                autor=random.choice(usuarios_obj),
                contenido=f"Comentario raíz #{i}",
                parent=None,
            )
            comentarios_creados.append(c)

        # 2) Respuestas a raíz
        for i in range(total_replies):
            parent = random.choice(comentarios_creados)
            c = Comentario.objects.create(
                queja=parent.queja,  # mantenemos coherencia
                autor=random.choice(usuarios_obj),
                contenido=f"Respuesta #{i} a comentario {parent.id}",
                parent=parent,
            )
            comentarios_creados.append(c)

        # 3) Respuestas profundas (a cualquiera de los existentes)
        for i in range(total_deep):
            parent = random.choice(comentarios_creados)
            c = Comentario.objects.create(
                queja=parent.queja,
                autor=random.choice(usuarios_obj),
                contenido=f"Respuesta profunda #{i} a comentario {parent.id}",
                parent=parent,
            )
            comentarios_creados.append(c)

        self.stdout.write(self.style.SUCCESS(f"Comentarios creados: {len(comentarios_creados)}"))

        # ============================================================
        #  ME GUSTA: MASIVOS (quejas + comentarios)
        # ============================================================
        ct_queja = ContentType.objects.get_for_model(Queja)
        ct_comentario = ContentType.objects.get_for_model(Comentario)

        likes_quejas = 0
        for q in todas_quejas:
            k = min(random.randint(5, 25), len(usuarios_obj))
            for u in random.sample(usuarios_obj, k):
                _, created = MeGusta.objects.get_or_create(
                    content_type=ct_queja,
                    object_id=q.id,
                    autor=u,
                )
                if created:
                    likes_quejas += 1

        likes_comentarios = 0
        for c in comentarios_creados:
            k = min(random.randint(0, 12), len(usuarios_obj))
            for u in random.sample(usuarios_obj, k):
                _, created = MeGusta.objects.get_or_create(
                    content_type=ct_comentario,
                    object_id=c.id,
                    autor=u,
                )
                if created:
                    likes_comentarios += 1

        self.stdout.write(
            self.style.SUCCESS(f"Likes OK. Quejas: {likes_quejas} | Comentarios: {likes_comentarios}")
        )

        # ============================================================
        #  IMÁGENES ALEATORIAS
        # ============================================================
        imagenes_prueba = ["1.png", "2.png", "3.png", "4.png"]
        imagenes_creadas = 0
        for q in todas_quejas:
            num_img = random.randint(0, 4)
            for _ in range(num_img):
                img_name = random.choice(imagenes_prueba)
                ruta = os.path.join(settings.MEDIA_ROOT, "imagenes_prueba", img_name)
                if os.path.exists(ruta):
                    with open(ruta, "rb") as f:
                        Imagen.objects.create(
                            content_type=ct_queja,
                            object_id=q.id,
                            imagen=File(f, name=img_name),
                        )
                        imagenes_creadas += 1

        self.stdout.write(self.style.SUCCESS(f"Imágenes creadas: {imagenes_creadas}"))

        # ============================================================
        #  VÍDEOS ALEATORIOS
        # ============================================================
        videos_prueba = ["video_ejemplo.mp4"]
        videos_creados = 0
        for q in todas_quejas:
            if random.random() < 0.45:
                vid_name = random.choice(videos_prueba)
                ruta = os.path.join(settings.MEDIA_ROOT, "videos_prueba", vid_name)
                if os.path.exists(ruta):
                    with open(ruta, "rb") as f:
                        Video.objects.create(
                            content_type=ct_queja,
                            object_id=q.id,
                            video=File(f, name=vid_name),
                        )
                        videos_creados += 1

        self.stdout.write(self.style.SUCCESS(f"Vídeos creados: {videos_creados}"))
        self.stdout.write(self.style.SUCCESS("✅ SEED COMPLETADO."))