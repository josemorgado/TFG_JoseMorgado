from calendar import c
import random
from venv import create
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from categoria.models import Categoria
from distrito.models import Distrito
from perfil.models import Perfil
from django.contrib.auth.models import User
from quejas.models import Queja
from megusta.models import MeGusta
from comentario.models import Comentario
from django.core.files import File
from django.conf import settings
import os
from imagen.models import Imagen
from video.models import MAX_VIDEOS, Video
from datetime import date


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        # Crear categorías de ejemplo
        categorias = [
            {"nombre": "Tecnología", "descripcion": "Categoría relacionada con tecnología."},
            {"nombre": "Salud", "descripcion": "Categoría relacionada con salud y bienestar."},
            {"nombre": "Deportes", "descripcion": "Categoría relacionada con deportes y actividades físicas."},
            {"nombre": "Educación", "descripcion": "Categoría relacionada con educación y aprendizaje."},
            {"nombre": "Entretenimiento", "descripcion": "Categoría relacionada con entretenimiento y ocio."},
            {"nombre": "Igualdad", "descripcion": "Categoría relacionada con igualdad de oportunidades y derechos.", "activo": False},
        ]
        created_count = 0
        for categoria_data in categorias:
            Categoria.objects.get_or_create(**categoria_data)
            created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} Categorías de ejemplo creadas exitosamente.'))

        # Crear distritos de ejemplo
        distritos = [
            {"nombre": "Centro", "codigo": "CTR"},
            {"nombre": "Norte", "codigo": "NTE"},
            {"nombre": "Sur", "codigo": "SUR"},
            {"nombre": "Este", "codigo": "EST"},
            {"nombre": "Oeste", "codigo": "OES"},
        ]
        created_count = 0
        for distrito_data in distritos:
            Distrito.objects.get_or_create(**distrito_data)
            created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} Distritos de ejemplo creados exitosamente.'))

        # Crear usuarios de ejemplo
        usuarios = [
            {
                "username": "josem",
                "email": "josemaria1.jmmp@gmail.com",
                "password": "1234",
                "first_name": "Jose Maria",
                "last_name": "Morgado Prudencio",
                "is_superuser": True,
                "is_staff": True,
                "perfil": {
                    "genero": "M",
                    "biografia": "Soy el creador del TFG",
                    "moderator": True,
                    "telefono": "+630974036",
                    "direccion": "Calle Fernando de Rojas 37",
                    "fecha_nacimiento": date(2003, 11, 20)
                }
            },
            {
                "username": "primo",
                "email": "primo@test.com",
                "password": "Password123",
                "first_name": "Primo",
                "last_name": "Morgado",
                "perfil": {
                    "genero": "M",
                    "biografia": "Soy primo y me encanta el TFG",
                    "moderator": False,
                    "telefono": "+34600123456",
                    "direccion": "Calle Falsa 123",
                    "fecha_nacimiento": date(2000, 7, 16)
                }
            },
            {
                "username": "mano",
                "email": "mano@test.com",
                "password": "Password123",
                "first_name": "Mano",
                "last_name": "Prudencio",
                "perfil": {
                    "genero": "F",
                    "biografia": "Hola, soy mano",
                    "moderator": True,
                    "telefono": "+34600654321",
                    "direccion": "Avenida Siempre Viva 456",
                    "fecha_nacimiento": date(2004, 4, 2)
                }
            }
        ]
        created_count = 0
        for usuario_data in usuarios:
            perfil_data = usuario_data.pop("perfil")
            password = usuario_data.pop("password")  # <--- quitar antes
            username = usuario_data["username"]

            user, created = User.objects.get_or_create(username=username, defaults=usuario_data)

            if created:
                user.set_password(password)  # <--- hashea la contraseña
                user.save()
                created_count += 1

            Perfil.objects.update_or_create(user=user, defaults=perfil_data)
        self.stdout.write(self.style.SUCCESS(f'{created_count} Usuarios de ejemplo creados exitosamente.'))

        # Crear quejas de ejemplo
        quejas = [
            {
                "titulo": "Falta de iluminación en el parque central",
                "descripcion": "El parque central del distrito norte está muy oscuro por las noches, lo que genera inseguridad para los vecinos.",
                "categoria": "Salud",
                "distrito": "Norte",
                "estado": "PEN",
                "ubicacion": "Parque Central, Distrito Norte",
                "autor": "primo"
            },
            {
                "titulo": "Baches en la calle principal",
                "descripcion": "La calle principal del distrito sur tiene muchos baches que dificultan el tránsito y dañan los vehículos.",
                "categoria": "Tecnología",
                "distrito": "Sur",
                "estado": "ENP",
                "ubicacion": "Calle Principal, Distrito Sur",
                "autor": "mano"
            },
            {
                "titulo": "Falta de áreas verdes en el distrito este",
                "descripcion": "El distrito este carece de áreas verdes y parques, lo que afecta la calidad de vida de los residentes.",
                "categoria": "Educación",
                "distrito": "Este",
                "estado": "RES",
                "ubicacion": "Distrito Este",
                "autor": "josem"
            },
            {
                "titulo": "Ruido excesivo en la zona de ocio",
                "descripcion": "La zona de ocio del distrito oeste genera mucho ruido durante la noche, lo que molesta a los vecinos.",
                "categoria": "Entretenimiento",
                "distrito": "Oeste",
                "estado": "REC",
                "ubicacion": "Zona de Ocio, Distrito Oeste",
                "autor": "primo"
            },
            {
                "titulo": "Falta de accesibilidad en el transporte público",
                "descripcion": "El transporte público del distrito centro no es accesible para personas con movilidad reducida.",
                "categoria": "Igualdad",
                "distrito": "Centro",
                "estado": "PEN",
                "ubicacion": "Transporte Público, Distrito Centro",
                "autor": "mano"
            },
            {
                "titulo": "Contenedores de basura desbordados",
                "descripcion": "Los contenedores del distrito norte están constantemente llenos y generan malos olores.",
                "categoria": "Salud",
                "distrito": "Norte",
                "estado": "ENP",
                "ubicacion": "Calles del distrito norte",
                "autor": "josem"
            },
            {
                "titulo": "Falta de señalización en cruces peligrosos",
                "descripcion": "Varios cruces del distrito sur carecen de señales y semáforos adecuados.",
                "categoria": "Tecnología",
                "distrito": "Sur",
                "estado": "RES",
                "ubicacion": "Cruces principales, Distrito Sur",
                "autor": "primo"
            },
            {
                "titulo": "Ruido de obras nocturnas",
                "descripcion": "Las obras en el distrito este continúan hasta altas horas de la noche, afectando el descanso de los vecinos.",
                "categoria": "Educación",
                "distrito": "Este",
                "estado": "REC",
                "ubicacion": "Barrio Este",
                "autor": "mano"
            },
            {
                "titulo": "Falta de limpieza en calles del centro",
                "descripcion": "Las calles del distrito centro presentan suciedad acumulada y basura en varias zonas.",
                "categoria": "Salud",
                "distrito": "Centro",
                "estado": "PEN",
                "ubicacion": "Calles principales, Distrito Centro",
                "autor": "josem"
            },
            {
                "titulo": "Canchas deportivas en mal estado",
                "descripcion": "Las instalaciones deportivas del distrito oeste están deterioradas y no se pueden usar.",
                "categoria": "Deportes",
                "distrito": "Oeste",
                "estado": "ENP",
                "ubicacion": "Polideportivo Distrito Oeste",
                "autor": "primo"
            },
            {
                "titulo": "Falta de programas educativos para jóvenes",
                "descripcion": "El distrito este no ofrece actividades educativas para adolescentes durante el verano.",
                "categoria": "Educación",
                "distrito": "Este",
                "estado": "RES",
                "ubicacion": "Centro Juvenil Distrito Este",
                "autor": "mano"
            },
            {
                "titulo": "Mobiliario urbano dañado",
                "descripcion": "Los bancos y farolas del distrito sur están rotos o dañados.",
                "categoria": "Tecnología",
                "distrito": "Sur",
                "estado": "REC",
                "ubicacion": "Plaza Mayor, Distrito Sur",
                "autor": "josem"
            },
            {
                "titulo": "Falta de señal wifi en zonas públicas",
                "descripcion": "El distrito centro carece de acceso wifi en plazas y parques públicos.",
                "categoria": "Tecnología",
                "distrito": "Centro",
                "estado": "PEN",
                "ubicacion": "Plaza Central, Distrito Centro",
                "autor": "primo"
            },
            {
                "titulo": "Falta de espacios culturales",
                "descripcion": "El distrito norte no cuenta con teatros ni salas de exposiciones accesibles a la comunidad.",
                "categoria": "Entretenimiento",
                "distrito": "Norte",
                "estado": "ENP",
                "ubicacion": "Barrio Norte",
                "autor": "mano"
            },
            {
                "titulo": "Poca accesibilidad para personas mayores",
                "descripcion": "El distrito oeste tiene muchas aceras en mal estado y escaleras sin rampas, dificultando el desplazamiento de personas mayores.",
                "categoria": "Igualdad",
                "distrito": "Oeste",
                "estado": "RES",
                "ubicacion": "Calles principales, Distrito Oeste",
                "autor": "josem"
            }
        ]
        created_count = 0
        for queja_data in quejas:
            categoria = Categoria.objects.get(nombre=queja_data.pop("categoria"))
            distrito = Distrito.objects.get(nombre=queja_data.pop("distrito"))
            autor = User.objects.get(username=queja_data.pop("autor"))

            queja, created = Queja.objects.get_or_create(
                titulo=queja_data["titulo"],
                descripcion=queja_data["descripcion"],
                categoria=categoria,
                distrito=distrito,
                estado=queja_data["estado"],
                ubicacion=queja_data["ubicacion"],
                autor=autor
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} Quejas de ejemplo creadas exitosamente.'))

        # Crear comentarios de ejemplo
        comentarios = [
            {
                "queja": "Falta de iluminación en el parque central",
                "autor": "primo",
                "contenido": "Es verdad, cada noche da miedo pasar por allí.",
                "parent": None
            },
            {
                "queja": "Falta de iluminación en el parque central",
                "autor": "mano",
                "contenido": "Deberían poner más farolas y cámaras de seguridad.",
                "parent": 1
            },
            {
                "queja": "Baches en la calle principal",
                "autor": "josem",
                "contenido": "He tenido que cambiar dos ruedas por culpa de estos baches.",
                "parent": None
            },
            {
                "queja": "Baches en la calle principal",
                "autor": "primo",
                "contenido": "A mí también me pasó lo mismo el mes pasado.",
                "parent": 3
            },
            {
                "queja": "Falta de áreas verdes en el distrito este",
                "autor": "mano",
                "contenido": "Sería genial tener un parque comunitario.",
                "parent": None
            },
            {
                "queja": "Falta de áreas verdes en el distrito este",
                "autor": "josem",
                "contenido": "Totalmente de acuerdo, la zona necesita más espacios verdes.",
                "parent": 5
            },
            {
                "queja": "Ruido excesivo en la zona de ocio",
                "autor": "primo",
                "contenido": "Es insoportable los fines de semana.",
                "parent": None
            },
            {
                "queja": "Ruido excesivo en la zona de ocio",
                "autor": "mano",
                "contenido": "La policía debería intervenir más seguido.",
                "parent": 7
            },
            {
                "queja": "Falta de accesibilidad en el transporte público",
                "autor": "josem",
                "contenido": "Muchos vecinos mayores tienen problemas para subir al autobús.",
                "parent": None
            },
            {
                "queja": "Falta de accesibilidad en el transporte público",
                "autor": "primo",
                "contenido": "Totalmente cierto, necesitamos rampas y elevadores.",
                "parent": 9
            },
            {
                "queja": "Falta de accesibilidad en el transporte público",
                "autor": "mano",
                "contenido": "Espero que lo solucionen pronto.",
                "parent": 10
            }
        ]
        created_count = 0
        for comentario_data in comentarios:
            queja = Queja.objects.get(titulo=comentario_data.pop("queja"))
            autor = User.objects.get(username=comentario_data.pop("autor"))
            parent_id = comentario_data.pop("parent")
            parent = Comentario.objects.get(id=parent_id) if parent_id else None

            comentario, created = Comentario.objects.get_or_create(
                queja=queja,
                autor=autor,
                contenido=comentario_data["contenido"],
                parent=parent
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} Comentarios de ejemplo creados exitosamente.'))

        # Crear 'me gusta' de ejemplo
        megustas = [
            {
            "model": "queja",
            "object_title": "Falta de iluminación en el parque central",
            "autor": ["josem", "mano"]
            },
            {
            "model": "queja",
            "object_title": "Baches en la calle principal",
            "autor": ["primo", "josem"]
            },
            {
            "model": "queja",
            "object_title": "Falta de áreas verdes en el distrito este",
            "autor": ["primo", "mano"]
            },
            {
            "model": "queja",
            "object_title": "Ruido excesivo en la zona de ocio",
            "autor": ["josem"]
            },
            {
            "model": "queja",
            "object_title": "Falta de accesibilidad en el transporte público",
            "autor": ["primo", "mano"]
            },
            {
            "model": "comentario",
            "object_content": "Es verdad, cada noche da miedo pasar por allí.",
            "autor": ["josem"]
            },
            {
            "model": "comentario",
            "object_content": "Deberían poner más farolas y cámaras de seguridad.",
            "autor": ["josem", "primo"]
            },
            {
            "model": "comentario",
            "object_content": "He tenido que cambiar dos ruedas por culpa de estos baches.",
            "autor": ["mano"]
            },
            {
            "model": "comentario",
            "object_content": "A mí también me pasó lo mismo el mes pasado.",
            "autor": ["josem"]
            },
            {
            "model": "comentario",
            "object_content": "Sería genial tener un parque comunitario.",
            "autor": ["josem", "primo"]
            },
            {
            "model": "comentario",
            "object_content": "Totalmente de acuerdo, la zona necesita más espacios verdes.",
            "autor": ["mano"]
            },
            {
            "model": "comentario",
            "object_content": "Es insoportable los fines de semana.",
            "autor": ["primo", "josem"]
            },
            {
            "model": "comentario",
            "object_content": "La policía debería intervenir más seguido.",
            "autor": ["josem"]
            }
        ]
        created_count = 0
        for megusta_data in megustas:
            model = megusta_data.pop("model")
            if model == "queja":
                obj = Queja.objects.get(titulo=megusta_data.pop("object_title"))
            elif model == "comentario":
                obj = Comentario.objects.get(contenido=megusta_data.pop("object_content"))
            else:
                continue  # Modelo no reconocido, saltar

            for username in megusta_data["autor"]:
                user = User.objects.get(username=username)

                ct = ContentType.objects.get_for_model(obj)

                instance, created = MeGusta.objects.get_or_create(
                    content_type=ct,
                    object_id=obj.id,
                    autor=user
                )
                if created:
                    created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} MeGusta de ejemplo creados exitosamente.'))

        # Crear imágenes de ejemplo
        imagenes_prueba = [
            "1.png",
            "2.png",
            "3.png",
            "4.png",
            "5.png",
            "6.png",
        ]
        ct_queja = ContentType.objects.get_for_model(Queja)
        created_count = 0
        for queja in Queja.objects.all():

            actuales = Imagen.objects.filter(
                content_type=ct_queja,
                object_id=queja.id
            ).count()

            if actuales >= 5:
                continue  # ya tiene el máximo

            max_a_crear = min(5 - actuales, 3)
            num_imagenes = random.randint(1, max_a_crear)

            usadas = random.sample(imagenes_prueba, k=num_imagenes)

            for nombre_imagen in usadas:
                ruta = os.path.join(
                    settings.MEDIA_ROOT,
                    "imagenes_prueba",
                    nombre_imagen
                )

                if not os.path.exists(ruta):
                    continue

                with open(ruta, "rb") as f:
                    Imagen.objects.get_or_create(
                        content_type=ct_queja,
                        object_id=queja.id,
                        imagen=File(f, name=nombre_imagen)
                    )

                    created_count += 1
        self.stdout.write(self.style.SUCCESS(f"{created_count} Imágenes de ejemplo creadas exitosamente."))

        # Crear videos de ejemplo
        videos_prueba = [
            "video_ejemplo.mp4",
        ]
        ct_queja = ContentType.objects.get_for_model(Queja)
        created_count = 0
        for queja in Queja.objects.all():
            actuales = Video.objects.filter(
                content_type=ct_queja,
                object_id=queja.id
            ).count()

            if actuales >= MAX_VIDEOS:
                continue

            max_a_crear = min(MAX_VIDEOS - actuales, 1)
            num_videos = random.randint(0, max_a_crear)

            if num_videos == 0:
                continue

            usadas = random.sample(videos_prueba, k=num_videos)

            for nombre_video in usadas:
                ruta = os.path.join(
                    settings.MEDIA_ROOT,
                    "videos_prueba",
                    nombre_video
                )

                if not os.path.exists(ruta):
                    continue

                with open(ruta, "rb") as f:
                    Video.objects.create(
                        content_type=ct_queja,
                        object_id=queja.id,
                        video=File(f, name=nombre_video)
                    )

                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"{created_count} Videos de ejemplo creados exitosamente."))

