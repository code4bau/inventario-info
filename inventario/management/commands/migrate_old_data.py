import sqlite3
# pyrefly: ignore [missing-import]
from django.core.management.base import BaseCommand
from inventario.models import Area, Persona, Item, Transaction
import os

class Command(BaseCommand):
    help = 'Migra datos desde el antiguo database.sqlite a Django'

    def handle(self, *args, **options):
        old_db_path = 'database.sqlite'
        if not os.path.exists(old_db_path):
            self.stdout.write(self.style.ERROR(f'No se encontró {old_db_path}'))
            return

        conn = sqlite3.connect(old_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Migrar Áreas
        self.stdout.write('Migrando áreas...')
        cursor.execute("SELECT * FROM areas")
        area_map = {} # old_id -> new_obj
        for row in cursor.fetchall():
            area, created = Area.objects.get_or_create(nombre=row['nombre_area'])
            area_map[row['id']] = area

        # Migrar Personas
        self.stdout.write('Migrando personas...')
        cursor.execute("SELECT * FROM personas")
        persona_map = {}
        for row in cursor.fetchall():
            persona, created = Persona.objects.get_or_create(
                nombre_completo=row['nombre_completo'],
                rol=row['rol']
            )
            persona_map[row['id']] = persona

        # Migrar Items
        self.stdout.write('Migrando ítems...')
        cursor.execute("SELECT * FROM items")
        item_map = {}
        for row in cursor.fetchall():
            item, created = Item.objects.get_or_create(
                codigo_patrimonial=row['codigo_patrimonial'],
                defaults={
                    'nombre': row['nombre'],
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion']
                }
            )
            item_map[row['id']] = item

        # Migrar Transacciones
        self.stdout.write('Migrando transacciones...')
        cursor.execute("SELECT * FROM transactions")
        for row in cursor.fetchall():
            try:
                Transaction.objects.get_or_create(
                    item=item_map[row['item_id']],
                    tipo=row['type'],
                    persona=persona_map[row['persona_id']],
                    area=area_map[row['area_id']],
                    observaciones=row['observaciones'],
                    timestamp=row['timestamp']
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error migrando transacción {row['id']}: {e}"))

        conn.close()
        self.stdout.write(self.style.SUCCESS('Migración completada con éxito'))
