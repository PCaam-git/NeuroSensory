# Proyecto NeuroSensory

Este proyecto es un sistema de gestión empresarial tipo miniERP especializado en la distribución de material terapéutico y de integración sensorial.

Está desarrollado con Django siguiendo el patrón MVT. La idea principal del proyecto es gestionar clientes, productos, pedidos, líneas de pedido y oportunidades comerciales, incorporando además validaciones, automatizaciones, una API REST y una configuración preparada para Docker.

---

## 1. Estructura general del proyecto

El proyecto está dividido en varias aplicaciones para separar responsabilidades y mantener el código organizado.

### App `core`

La app `core` contiene los datos maestros del sistema:

- `Cliente`
- `Producto`

Son entidades que existen por sí mismas dentro del ERP. Por ejemplo, un producto puede estar registrado aunque todavía no se haya vendido, y un cliente puede existir aunque todavía no tenga pedidos.

### App `ventas`

La app `ventas` contiene la parte transaccional del sistema:

- `Pedido`
- `LineaPedido`

Aquí se gestiona la lógica principal de ventas: pedidos, líneas de pedido, cálculo de totales, estados del pedido y actualización del stock.

### App `crm`

La app `crm` se ha añadido en esta nueva versión del proyecto.

Contiene el modelo:

- `Oportunidad`

Sirve para gestionar posibles ventas antes de que exista un pedido confirmado. Es decir, permite hacer seguimiento comercial de propuestas, negociaciones y oportunidades ganadas o perdidas.

### Proyecto `minierp`

La carpeta `minierp` contiene la configuración general del proyecto Django:

- `settings.py`
- `urls.py`
- `wsgi.py`

---

## 2. Modelo de datos

### 2.1. Entidades principales

El sistema trabaja con tres grupos de entidades.

Por un lado están los datos maestros:

- `Cliente`
- `Producto`

Por otro lado están los datos transaccionales:

- `Pedido`
- `LineaPedido`

Y, en esta nueva versión, se añade el módulo CRM:

- `Oportunidad`

Los maestros representan información estable del sistema. Los pedidos y líneas de pedido representan operaciones de venta. Las oportunidades representan posibles ventas que todavía no se han convertido en pedidos.

---

## 2.2. Relaciones entre entidades

### Cliente y Pedido

Un cliente puede tener muchos pedidos.

Un pedido pertenece a un único cliente.

La relación se ha configurado con:

```python
on_delete=models.RESTRICT
```

Esto significa que no se puede eliminar un cliente si ya tiene pedidos asociados. Esta decisión protege el historial de ventas.

---

### Pedido y LineaPedido

Un pedido puede tener muchas líneas de pedido.

Cada línea pertenece a un único pedido.

La relación se ha configurado con:

```python
on_delete=models.CASCADE
```

Esto significa que si se elimina un pedido, se eliminan también sus líneas. Tiene sentido porque una línea de pedido no aporta información útil sin su pedido.

---

### Producto y LineaPedido

Un producto puede aparecer en muchas líneas de pedido.

Cada línea de pedido hace referencia a un único producto.

La relación se ha configurado con:

```python
on_delete=models.RESTRICT
```

Esto evita eliminar productos que ya han sido utilizados en pedidos.

---

### Cliente y Oportunidad

Un cliente puede tener varias oportunidades comerciales asociadas.

Cada oportunidad pertenece a un único cliente.

Esta relación permite saber qué propuestas o posibles ventas se han trabajado con cada cliente.

---

## 2.3. Decisiones de diseño

### Claves primarias

Se utilizan los identificadores automáticos de Django como clave primaria.

Además, se han añadido campos únicos para evitar duplicados de negocio:

- `nif` en `Cliente`
- `sku` en `Producto`

Así se evita registrar dos veces el mismo cliente o el mismo producto.

---

### Snapshot en las líneas de pedido

La entidad `LineaPedido` guarda una copia de algunos datos del producto en el momento de la venta:

- descripción
- precio unitario
- tipo de IVA

Esto es importante porque los datos de un producto pueden cambiar con el tiempo.

Por ejemplo, si un producto cambia de precio en el futuro, los pedidos antiguos deben conservar el precio que tenía el producto cuando se realizó la venta.

---

### Validaciones de base de datos

Se han incluido restricciones para mantener la coherencia de los datos.

Por ejemplo:

- la cantidad de una línea de pedido debe ser mayor que cero;
- el total del pedido no puede ser negativo.

Estas validaciones ayudan a proteger la integridad del sistema.

---

### Índices

Se han añadido índices para mejorar las búsquedas más habituales:

- búsqueda por `nif` en clientes;
- búsqueda por `sku` en productos;
- búsqueda por nombre de producto;
- consulta de pedidos por cliente y fecha.

---

## 3. Formularios y validación

En esta versión se han añadido formularios personalizados con `ModelForm`.

El objetivo es validar los datos en el servidor y no depender solo de las restricciones del navegador.

### ProductoForm

El formulario de producto valida que el stock no pueda ser negativo.

Si se intenta guardar un producto con stock inferior a cero, el formulario muestra un error y no permite guardar.

Regla aplicada:

```text
stock >= 0
```

### ClienteForm

El formulario de cliente valida que el NIF/CIF sea único.

El enunciado permitía dos opciones: validar email corporativo o validar CIF único. En este proyecto se ha elegido la segunda opción porque NeuroSensory puede vender tanto a empresas como a particulares.

Además, esta validación encaja con el modelo real del proyecto, donde el campo `nif` ya está marcado como único.

### Uso en Django Admin

Estos formularios se han conectado con el panel de administración de Django.

De esta forma, las validaciones se aplican directamente desde las pantallas de gestión de clientes y productos.

---

## 4. Cálculo automático de totales

El modelo `Pedido` incorpora el método:

```python
calcular_totales()
```

Este método calcula automáticamente los importes del pedido a partir de sus líneas.

### Cálculos realizados

El cálculo se hace a partir de las líneas del pedido:

```text
Base imponible = cantidad x precio_unitario
IVA = base_linea x tipo_iva
Total neto = total_bruto + total_iva
```

El sistema recorre las líneas del pedido y acumula los importes.

### Uso de Decimal

Para los importes económicos se utiliza `Decimal`.

Esto evita problemas de precisión que podrían aparecer si se usaran números decimales de tipo `float`.

### IVA por línea

Aunque el ejemplo habitual usa un IVA del 21%, este proyecto guarda el IVA aplicado en cada línea.

Esto permite respetar el diseño del proyecto, ya que cada producto puede tener su propio tipo de IVA.

### Actualización automática

Cada vez que se guarda o elimina una línea de pedido, se recalculan los totales del pedido.

Así se evita que el total bruto, el IVA o el total neto queden desactualizados.

---

## 5. Automatización con signals

Se ha añadido una automatización mediante señales de Django.

El objetivo es descontar automáticamente el stock de los productos cuando un pedido pasa al estado:

```text
CONFIRMADO
```

### Funcionamiento

Se utilizan dos señales:

- `pre_save`
- `post_save`

La señal `pre_save` guarda temporalmente el estado anterior del pedido.

La señal `post_save` comprueba si el pedido acaba de pasar a `CONFIRMADO`.

Esto evita que el stock se descuente más de una vez si se vuelve a guardar un pedido que ya estaba confirmado.

### Flujo aplicado

```text
Pedido en BORRADOR
    No descuenta stock

Pedido pasa de BORRADOR a CONFIRMADO
    Descuenta stock

Pedido ya confirmado y se vuelve a guardar
    No descuenta stock otra vez
```

### Stock insuficiente

Si el pedido se confirma pero no hay stock suficiente, el sistema no descuenta stock.

En su lugar, registra un error en la terminal mediante logs.

Ejemplo:

```text
Stock insuficiente para confirmar el pedido 9. Producto: 5625125. Stock actual: 3. Cantidad solicitada: 6.
```

Esta decisión evita descuentos parciales y permite que el administrador revise la incidencia.

---

## 6. Módulo CRM

En esta nueva versión se ha creado la app `crm`.

Esta app permite gestionar oportunidades comerciales antes de que exista un pedido confirmado.

### Modelo Oportunidad

El modelo `Oportunidad` contiene los siguientes campos:

- `titulo`
- `cliente`
- `valor_estimado`
- `etapa`
- `fecha_creacion`
- `fecha_cierre`

También incluye propiedades calculadas, como los días que la oportunidad lleva abierta.

### Etapas del pipeline

Las etapas disponibles son:

1. Prospección
2. Propuesta
3. Negociación
4. Cerrada Ganada
5. Cerrada Perdida

Este flujo permite representar el recorrido de una oportunidad desde que se detecta hasta que se gana o se pierde.

### Fecha de creación y fecha de cierre

La fecha de creación se genera automáticamente.

La fecha de cierre puede dejarse vacía mientras la oportunidad siga abierta.

Cuando una oportunidad se cierra, puede indicarse la fecha correspondiente.

---

## 7. KPI de tasa de conversión

El módulo CRM permite definir el KPI de tasa de conversión.

Este indicador mide qué porcentaje de oportunidades comerciales terminan en éxito.

La fórmula es:

```text
Tasa de Conversión = (Oportunidades Ganadas / Total de Oportunidades) x 100
```

En este proyecto:

- las oportunidades ganadas son las que están en etapa `Cerrada Ganada`;
- el total de oportunidades es el número total de oportunidades registradas.

Ejemplo:

```text
Si hay 10 oportunidades y 4 están cerradas como ganadas:

Tasa de Conversión = (4 / 10) x 100 = 40%
```

Este KPI ayuda a analizar la eficacia comercial del sistema.

---

## 8. API REST con Django REST Framework

El proyecto incorpora una API REST usando Django REST Framework.

### Endpoint disponible

```text
/api/productos/
```

Este endpoint devuelve el listado de productos en formato JSON.

### Estructura utilizada

La API se ha organizado en varios archivos:

```text
core/serializers.py
core/permissions.py
core/api_views.py
minierp/urls.py
```

Esta separación ayuda a mantener el código claro.

### Protección del stock

El campo `stock` se considera información interna del ERP.

Por eso la API funciona de esta forma:

```text
Usuario no autenticado
    Puede ver productos, pero no ve stock.

Usuario autenticado
    Puede ver productos y también el stock.
```

De esta manera, se permite consultar el catálogo sin exponer información sensible de almacén.

### Métodos permitidos

La API de productos es de solo lectura.

Permite:

```text
GET
HEAD
OPTIONS
```

---

## 9. Datos de prueba

El proyecto incluye un comando personalizado para generar datos de prueba.

### Herramienta utilizada

```text
Faker
```

### Comando

```bash
python manage.py seed_db
```

Este comando genera clientes y productos ficticios para poder probar el sistema desde el panel de administración.

Los datos de prueba permiten comprobar más fácilmente:

- clientes;
- productos;
- stock;
- pedidos;
- API.

---

## 10. Panel de administración

El proyecto utiliza Django Admin como interfaz principal de gestión.

### Clientes

Desde el admin se pueden crear y editar clientes.

Se muestran datos como:

- NIF/CIF
- razón social
- email
- teléfono
- fecha de creación

También se puede buscar por razón social o NIF/CIF.

### Productos

Desde el admin se pueden crear y editar productos.

Se muestran datos como:

- SKU
- nombre
- precio
- IVA
- stock

También se puede buscar por SKU o nombre, y filtrar por tipo de IVA.

### Pedidos

Desde el admin se pueden crear y editar pedidos.

Las líneas de pedido aparecen dentro del propio pedido mediante un inline.

Los totales se muestran como campos de solo lectura.

### Oportunidades

Desde el admin se pueden crear y editar oportunidades comerciales.

Se muestran:

- título
- cliente
- valor estimado
- etapa
- fecha de creación
- fecha de cierre
- días abierta

También se puede filtrar por etapa y buscar por cliente.

---

## 11. Variables de entorno

El proyecto usa variables de entorno para separar la configuración sensible del código.

Para ello se utiliza:

```text
python-dotenv
```

### `.env.example`

El archivo `.env.example` sirve como plantilla.

Sí se incluye en el repositorio.

Ejemplo:

```env
DEBUG=False
SECRET_KEY=change-me-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=neurosensory_db
DB_USER=neurosensory_user
DB_PASS=neurosensory_pass
DB_HOST=db
DB_PORT=5432
```

### `.env`

El archivo `.env` contiene los valores reales de cada entorno.

No debe subirse al repositorio.

Está incluido en `.gitignore`.

---

## 12. Base de datos

El proyecto puede trabajar con dos bases de datos según el entorno.

### Desarrollo local

En local, si no se configuran variables de PostgreSQL, el proyecto usa SQLite:

```text
db.sqlite3
```

Esto facilita el desarrollo y las pruebas rápidas.

### Docker

Cuando se ejecuta con Docker, el proyecto usa PostgreSQL.

La configuración se obtiene desde las variables de entorno definidas en `.env`.

---

## 13. Dockerización

El proyecto se ha preparado para ejecutarse con Docker.

### Archivos principales

```text
Dockerfile
docker-compose.yml
.env.example
.dockerignore
requirements.txt
```

### Dockerfile

El `Dockerfile` construye la imagen de la aplicación Django.

Hace lo siguiente:

- parte de una imagen base de Python;
- copia `requirements.txt`;
- instala las dependencias;
- copia el código del proyecto;
- ejecuta `collectstatic`;
- arranca la aplicación con Gunicorn.

### docker-compose.yml

El archivo `docker-compose.yml` levanta dos servicios:

- `db`
- `web`

El servicio `db` utiliza PostgreSQL.

El servicio `web` contiene la aplicación Django.

### Healthcheck

Se ha añadido un `healthcheck` al servicio de PostgreSQL.

Esto permite que la aplicación espere a que la base de datos esté preparada antes de arrancar.

### WhiteNoise y archivos estáticos

Se ha añadido WhiteNoise para servir archivos estáticos cuando `DEBUG=False`.

Durante la construcción de la imagen se ejecuta:

```bash
python manage.py collectstatic --noinput
```

Los archivos estáticos se recopilan en:

```text
staticfiles/
```

Esto permite que el admin y la API de Django REST Framework se vean correctamente con estilos dentro de Docker.

---

## 14. Instalación y uso en local

### Requisitos

- Python 3.13
- pip
- Git

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
```

Entrar en la carpeta donde está `manage.py`.

### 2. Crear y activar entorno virtual

En Windows:

```bash
python -m venv env
.\env\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Cargar datos de prueba

```bash
python manage.py seed_db
```

### 7. Levantar servidor

```bash
python manage.py runserver
```

### 8. Acceder al admin

```text
http://127.0.0.1:8000/admin/
```

### 9. Probar la API

```text
http://127.0.0.1:8000/api/productos/
```

---

## 15. Ejecución con Docker

### 1. Crear archivo `.env`

Crear un archivo `.env` a partir de `.env.example`.

Ejemplo:

```env
DEBUG=False
SECRET_KEY=neurosensory-docker-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=neurosensory_db
DB_USER=neurosensory_user
DB_PASS=neurosensory_pass
DB_HOST=db
DB_PORT=5432
```

### 2. Construir la imagen

```bash
docker compose build
```

### 3. Levantar los contenedores

```bash
docker compose up
```

### 4. Crear superusuario dentro del contenedor

En otra terminal:

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Acceder al admin

```text
http://127.0.0.1:8000/admin/
```

### 6. Probar la API

```text
http://127.0.0.1:8000/api/productos/
```

Si la base de datos PostgreSQL está recién creada, la API puede devolver una lista vacía:

```json
[]
```

Esto es normal porque la base de datos de Docker es distinta de `db.sqlite3`.

---

## 16. Tecnologías utilizadas

- Python 3.13
- Django 5.2.8
- Django REST Framework
- SQLite
- PostgreSQL
- Faker
- python-dotenv
- psycopg2-binary
- Gunicorn
- WhiteNoise
- Docker
- Docker Compose

---

## 17. Funcionalidades añadidas en esta versión

En esta versión del miniERP se han añadido las siguientes mejoras:

- formularios personalizados para clientes y productos;
- validación de stock no negativo;
- validación de NIF/CIF único;
- cálculo automático de totales de pedido;
- automatización de stock mediante signals;
- módulo CRM con oportunidades comerciales;
- KPI de tasa de conversión;
- API REST de productos;
- protección del stock para usuarios autenticados;
- configuración mediante variables de entorno;
- dockerización con PostgreSQL;
- servicio de estáticos con WhiteNoise.

---

## 18. Notas finales

El proyecto mantiene una estructura sencilla y académica.

Las decisiones principales se han tomado buscando claridad y facilidad de defensa.

Se mantiene SQLite para el trabajo local porque facilita el desarrollo.

Se utiliza PostgreSQL en Docker para cumplir el requisito de despliegue de la actividad.

La configuración sensible se separa del código mediante variables de entorno.

El archivo `.env` no se sube al repositorio.

El archivo `.env.example` sirve como plantilla para configurar el proyecto en otros equipos.
