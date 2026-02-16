from django.core.management.base import BaseCommand
from django.conf import settings
import psycopg2


class Command(BaseCommand):
    help = "Borra y crea la base de datos (SOLO LOCAL)"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise Exception("No puedes usar resetdb en producción")
        db = settings.DATABASES["default"]

        db_name = db["NAME"]
        db_user = db["USER"]
        db_password = db["PASSWORD"]
        db_host = db["HOST"]
        db_port = db["PORT"]

        self.stdout.write(self.style.WARNING(f"⚠️  Borrando base de datos {db_name}..."))

        # Conectamos a postgres (NO a la BD del proyecto)
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Cerrar conexiones activas
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_name}'
              AND pid <> pg_backend_pid();
        """)

        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        cursor.execute(f"CREATE DATABASE {db_name};")

        cursor.close()
        conn.close()

        self.stdout.write(self.style.SUCCESS("✅ Base de datos recreada"))

        # Migraciones
        from django.core.management import call_command
        call_command("migrate")

        # Opcional: seed
        # call_command("seed")

        self.stdout.write(self.style.SUCCESS("🚀 Proyecto listo"))
