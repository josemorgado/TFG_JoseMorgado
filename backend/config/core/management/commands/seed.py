import random
from datetime import date, timedelta

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from categoria.models import Categoria
from comentario.models import Comentario
from distrito.models import Distrito
from megusta.models import MeGusta
from perfil.models import Perfil
from quejas.models import Queja
from respuesta.models import Respuesta


class Command(BaseCommand):
    help = "Seed optimizado para desarrollo local (rápido, realista y estable)"

    def handle(self, *args, **kwargs):

        # ============================================================
        # TRUNCATE TODAS LAS TABLAS
        # ============================================================
        with connection.cursor() as cursor:
            for model in apps.get_models():
                cursor.execute(
                    f'TRUNCATE TABLE "{model._meta.db_table}" RESTART IDENTITY CASCADE;'
                )
        self.stdout.write(self.style.SUCCESS("TRUNCATE OK"))

        # ============================================================
        # CATEGORÍAS
        # ============================================================
        categorias_data = [
            ("Tecnología", "Tecnología y digitalización"),
            ("Salud", "Salud pública"),
            ("Educación", "Educación y centros educativos"),
            ("Infraestructura", "Calles y obras"),
            ("Transporte", "Movilidad urbana"),
            ("Servicios Públicos", "Limpieza, alumbrado, ruido"),
        ]

        Categoria.objects.bulk_create(
            [Categoria(nombre=n, descripcion=d) for n, d in categorias_data]
        )
        categorias = list(Categoria.objects.all())
        self.stdout.write(self.style.SUCCESS("Categorías OK"))

        # ============================================================
        # DISTRITOS
        # ============================================================
        distritos_data = [
            ("Centro", "CTR"),
            ("Norte", "NTE"),
            ("Sur", "SUR"),
            ("Este", "EST"),
            ("Oeste", "OES"),
        ]

        Distrito.objects.bulk_create(
            [Distrito(nombre=n, codigo=c) for n, c in distritos_data]
        )
        distritos = list(Distrito.objects.all())
        self.stdout.write(self.style.SUCCESS("Distritos OK"))

        # ============================================================
        # USUARIOS Y PERFILES
        # ============================================================
        usuarios = []

        admin = User(
            username="josem",
            email="josemaria1.jmmp@gmail.com",
            first_name="José María",
            last_name="Morgado Prudencio",
            is_superuser=True,
            is_staff=True,
        )
        admin.set_password("1234")
        usuarios.append(admin)

        for i in range(1, 25):
            u = User(
                username=f"user{i}",
                email=f"user{i}@test.com",
                first_name=f"Usuario{i}",
                last_name="Demo",
            )
            u.set_password("1234")
            usuarios.append(u)

        User.objects.bulk_create(usuarios)
        usuarios = list(User.objects.all())

        perfiles = []
        for u in usuarios:
            perfiles.append(
                Perfil(
                    user=u,
                    genero=random.choice(["M", "F"]),
                    biografia="Usuario de prueba",
                    moderator=u.is_superuser or random.random() < 0.2,
                    fecha_nacimiento=date(1995, 1, 1),
                )
            )

        Perfil.objects.bulk_create(perfiles)
        self.stdout.write(self.style.SUCCESS(f"Usuarios OK ({len(usuarios)})"))

        # ============================================================
        # QUEJAS
        # ============================================================
        ahora = timezone.now()
        quejas = []

        for i in range(80):
            creada = ahora - timedelta(days=random.randint(1, 120))
            quejas.append(
                Queja(
                    titulo=f"Queja #{i}",
                    descripcion="Descripción de prueba",
                    categoria=random.choice(categorias),
                    distrito=random.choice(distritos),
                    estado=random.choice(["PEN", "ENP", "REC", "RES"]),
                    ubicacion="Ubicación genérica",
                    autor=random.choice(usuarios),
                    fecha_creacion=creada,
                    fecha_actualizacion=creada + timedelta(days=random.randint(0, 10)),
                )
            )

        Queja.objects.bulk_create(quejas)
        quejas = list(Queja.objects.all())
        self.stdout.write(self.style.SUCCESS(f"Quejas OK ({len(quejas)})"))

        # ============================================================
        # COMENTARIOS (2 FASES: RAÍZ + RESPUESTAS)
        # ============================================================
        comentarios_root = []

        for q in quejas:
            for _ in range(random.randint(0, 2)):
                comentarios_root.append(
                    Comentario(
                        queja=q,
                        autor=random.choice(usuarios),
                        contenido="Comentario raíz",
                        parent=None,
                    )
                )

        Comentario.objects.bulk_create(comentarios_root)
        comentarios_root = list(
            Comentario.objects.filter(parent__isnull=True)
        )

        comentarios_respuestas = []

        for parent in comentarios_root:
            if random.random() < 0.5:
                comentarios_respuestas.append(
                    Comentario(
                        queja=parent.queja,
                        autor=random.choice(usuarios),
                        contenido="Respuesta a comentario",
                        parent=parent,
                    )
                )

        Comentario.objects.bulk_create(comentarios_respuestas)

        comentarios = comentarios_root + comentarios_respuestas
        self.stdout.write(
            self.style.SUCCESS(f"Comentarios OK ({len(comentarios)})")
        )

        # ============================================================
        # ME GUSTA (BULK_CREATE)
        # ============================================================
        ct_queja = ContentType.objects.get_for_model(Queja)
        ct_comentario = ContentType.objects.get_for_model(Comentario)

        likes = []

        for q in random.sample(quejas, k=min(40, len(quejas))):
            for u in random.sample(usuarios, k=5):
                likes.append(
                    MeGusta(
                        content_type=ct_queja,
                        object_id=q.id,
                        autor=u,
                    )
                )

        for c in random.sample(comentarios, k=min(60, len(comentarios))):
            for u in random.sample(usuarios, k=3):
                likes.append(
                    MeGusta(
                        content_type=ct_comentario,
                        object_id=c.id,
                        autor=u,
                    )
                )

        MeGusta.objects.bulk_create(likes, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Likes OK ({len(likes)})"))

        # ============================================================
        # RESPUESTAS OFICIALES
        # ============================================================
        moderadores = [u for u in usuarios if u.perfil.moderator]
        respuestas = []

        for q in random.sample(quejas, k=min(40, len(quejas))):
            respuestas.append(
                Respuesta(
                    queja=q,
                    moderador=random.choice(moderadores),
                    contenido="Respuesta oficial del ayuntamiento",
                    nuevo_estado=random.choice(["ENP", "REC", "RES"]),
                    fecha_respuesta=q.fecha_creacion
                    + timedelta(days=random.randint(1, 30)),
                )
            )

        Respuesta.objects.bulk_create(respuestas)
        self.stdout.write(self.style.SUCCESS(f"Respuestas OK ({len(respuestas)})"))

        self.stdout.write(self.style.SUCCESS("✅ SEED FAST COMPLETADO"))