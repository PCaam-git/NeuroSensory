from django.core.management.base import BaseCommand
from faker import Faker
from core.models import Cliente, Producto
import random

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba falsos pero realistas'

    def handle(self, *args, **kwargs):
        fake = Faker('es_ES') # Configuración de idioma España
        
        self.stdout.write('🌱 Sembrando datos para NeuroSensory...')

        # --- 1. CREAR CLIENTES ---
        self.stdout.write('Creando Clientes...')
        for _ in range(10): # Crea 10 clientes
            # Faker genera DNIs, nombres y empresas falsas
            Cliente.objects.get_or_create(
                nif=fake.unique.nie(), # NIE/NIF único
                defaults={
                    'razon_social': fake.company(),
                    'email': fake.company_email(),
                    'telefono': fake.phone_number(),
                    'direccion': fake.address()
                }
            )

        # --- 2. CREAR PRODUCTOS ---
        self.stdout.write('Creando Productos...')
        # Prefijos =  material terapéutico
        prefijos = ['Manta', 'Cojín', 'Chaleco', 'Pelota', 'Mordedor', 'Panel']
        adjetivos = ['Sensorial', 'Ponderado', 'Táctil', 'Visual', 'Propioceptivo']

        for _ in range(15): # Crea 15 Productos
            nombre_prod = f"{random.choice(prefijos)} {random.choice(adjetivos)}"
            sku_random = f"REF-{random.randint(1000, 9999)}"
            
            Producto.objects.get_or_create(
                sku=sku_random,
                defaults={
                    'nombre': nombre_prod,
                    'descripcion': fake.text(max_nb_chars=100),
                    'precio': round(random.uniform(10.0, 150.0), 2), # Precio entre 10 y 150
                    'stock': random.randint(0, 100)
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ ¡Base de datos regada y abonada con éxito!'))