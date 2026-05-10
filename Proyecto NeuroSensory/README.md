Proyecto NeuroSensory

Este proyecto es un sistema de gestión empresarial (miniERP) especializado en la distribución de material terapéutico y de integración sensorial.
El proyecto se ha desarrollado con Django siguiendo el patrón MVT.

1. ESTRUCTURA DEL PROYECTO.

El sistema se divide en dos aplicaciones principales para separar responsabilidades:
    - App 'core' (maestros): desde aquí se gestionan las entidades estáticas que apenas sufren cambios en el tiempo (clientesy productos).
    - App 'ventas' (transaccional): aquí se gestiona la lógica del negocio diaria, la facturación y los movimientos de stock (pedidos y líneas).


2. JUSTIFICACIÓN DEL MODELO DE DATOS.

    2.1 Entidades y roles
    - Maestros (cliente, producto): Se consideran maestros porque existen de forma independiente. Un producto existe en el almacén aunque nunca se haya vendido. Están protegidos con restricciones 'unique' en sus claves 'NIF' Y 'SKU' para garantizar la integridad.

    - Transaccionales (pedido, líneaPedido): surgen de la actividad diaria. Utilizan claves foráneas (ForeignKey) para relacionarse con los maestros.


    2.2 Relaciones y cardinalidad
    - Cliente 1:N Pedido: Un cliente puede realizar múltiples pedidos a lo largo del tiempo, pero un pedido está asociado a un único cliente.
        - Política de borrado: 'restrict'. No se permite eliminar un cliente si tiene historial de pedidos.

    - Pedido 1:N LineaPedido: Un pedido se compone por una o muchas líneas de artículos o detalle. 
        - Política de borrado: 'cascade'. Si se elimina un pedido, se eliminan todas sus líneas, ya que no tienen sentido por si solas y no aportan información sin su pedido.

    - Producto 1:N LineaPedido: cada línea de pedido únicamente tendrá un producto mientras que un producto puede aparecer en infinitas líneas de pedido.
        - Política de borrado: 'restrict'. No se puede eliminar un producto del catálogo si se ha vendido en alguna ocasión.

    
    2.3 Decisiones de diseño.
    - Claves primarias: Se utilizan claves surrogadas (el id autoincremental de Django) como clave primaria en todas las tablas. Adicionalmente, se marcan como UNIQUE los campos naturales (nif en Cliente, sku en Producto) para evitar duplicados de negocio.
    
    - Snapshot de precio: La entidad LineaPedido guarda una copia del precio, descripción e IVA en el momento de la venta (utilizando sobreescritura del método save). Esto evita que cambios futuros en el precio base del producto alteren facturas pasadas.
    
    - Validaciones: Se ha implementado un CheckConstraint a nivel de base de datos para asegurar que la cantidad en las líneas sea siempre positiva (> 0) y que los totales del pedido no sean negativos.
    
    - Índices: Se han definido índices para optimizar las consultas más frecuentes:
        - Índice único en nif (Cliente) y sku (Producto) para búsquedas rápidas por clave natural.
        - Índice compuesto (cliente_id, fecha) en Pedido para consultas de historial por cliente.
        - Índice simple en nombre (Producto) para búsquedas por texto.


    3. DIAGRAMA ENTIDAD-RELACIÓN
    El siguiente diagrama muestra la estructura de la base de datos, las relaciones entre tablas y las políticas de integridad referencial:
    ![alt text](image.png) 

    Leyenda de relaciones:
        Cliente 1:N Pedido: Un cliente puede tener múltiples pedidos (ON DELETE RESTRICT)
        Pedido 1:N LineaPedido: Un pedido contiene varias líneas (ON DELETE CASCADE)
        Producto 1:N LineaPedido: Un producto puede aparecer en múltiples líneas (ON DELETE RESTRICT)

    4. AUTOMATIZACIÓN Y DATOS DE PRUEBA (SEEDING)
    El proyecto incluye un comando personalizado para poblar la base de datos con datos ficticios pero realistas, facilitando las pruebas de carga y la visualización del entorno en el panel de administración (http://127.0.0.1:8000/admin/).

    Herramienta: librería Faker.
    Funcionalidad: genera automáticamente clientes con NIFs únicos y productos con precios, descripciones y stock aleatorios.
    Ejecución: desde la terminal, con el entorno virtual activado → python manage.py seed_db. Este comando, junto con la información que hemos añadido al archivo seed_db.py, genera automáticamente clientes con NIFs únicos y productos con precios y stock aleatorios.

    5. CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN
    - Cliente(Admin): Muestra NIF, razón social, email y teléfono. Permite búsqueda por razón social y NIF.
    - Producto(Admin): Muestra SKU, nombre, precio, IVA y stock. Incluye filtros por tipo de IVA y búsqueda por SKU y nombre.
    - Pedido(Admin): Muestra cliente, fecha, estado y total. Permite filtrar por estado y fecha. 

    6. MÓDULO CRM Y PIPELINE DE OPORTUNIDADES

    El proyecto incorpora una nueva aplicación llamada `crm`, encargada de gestionar oportunidades comerciales antes de que exista un pedido confirmado.

    A diferencia del módulo de ventas, que registra pedidos ya creados, el módulo CRM permite hacer seguimiento de posibles ventas durante su proceso de negociación.

        ### Modelo Oportunidad

    El modelo `Oportunidad` contiene los siguientes campos principales:

    - `titulo`: nombre o descripción breve de la oportunidad comercial.
    - `cliente`: cliente asociado a la oportunidad.
    - `valor_estimado`: importe económico previsto si la oportunidad se convierte en venta.
    - `etapa`: fase actual dentro del pipeline comercial.
    - `fecha_creacion`: fecha en la que se registra la oportunidad.
    - `fecha_cierre`: fecha en la que se cierra la oportunidad, si ya ha finalizado.

    ### Etapas del pipeline

    Las etapas definidas para una oportunidad son:

    1. Prospección
    2. Propuesta
    3. Negociación
    4. Cerrada Ganada
    5. Cerrada Perdida

    Este flujo representa el recorrido de una oportunidad desde que se detecta una posible venta hasta que finaliza como ganada o perdida.

    ### KPI: Tasa de Conversión

    La Tasa de Conversión mide qué porcentaje de oportunidades comerciales terminan en éxito.

    La fórmula es:

    ```text
    Tasa de Conversión = (Oportunidades Ganadas / Total de Oportunidades) × 100

    7. INSTALACIÓN Y USO
    Requisitos previos

    Python 3.8+
    pip

    Pasos de instalación

    1.Clonar el repositorio:

    bash   git clone <url-del-repositorio>
    cd neurosensory

    2.Crear y activar entorno virtual:

    bash   python -m venv venv
    
    # En Windows:
    .\venv\Scripts\activate
    
    # En macOS/Linux:
    source venv/bin/activate

    3.Instalar dependencias:

    bash   pip install django faker

    4.Aplicar migraciones:

    bash   python manage.py migrate

    5.Crear superusuario:

    bash   python manage.py createsuperuser

    6.(Opcional) Cargar datos de prueba:

    bash   python manage.py seed_db

    7.Ejecutar el servidor:

    bash   python manage.py runserver

    Acceder al panel de administración:

    URL: http://127.0.0.1:8000/admin/
    Usar las credenciales del superusuario creado en el paso 5




8. TECNOLOGÍAS UTILIZADAS

    Django 5.2.8: Framework web de Python
    Python 3.13.9: Lenguaje de programación
    SQLite: Base de datos (desarrollo)
    Faker 38.2.0: Generación de datos de prueba