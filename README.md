# Info Pibes S.A
Contenido de las prácticas:
## Práctica 1 :gear:
_**Diseño y desarrollo de un Sistema de Información sobre una temática (Red social).**_

- Nombre del sistema
- Descripción de cada subsistema.
- Desarrollo de requisitos para cada subsistema
    - Requisitos funcionales con sus requisitos de datos
    - Restricciones semánticas.

> [!WARNING] 
Falta los requisitos semánticos de la parte de usuarios

## Práctica 2 :gear:
_**Diseño de diagramas de flujo de datos y de esquemas externos para cada subsistema.**_
- DFDs de cada subsistema (Caja negra, armazón, DFD1 de cada susbsistema)
-  Esquemas externos de todos los procesos y almacenes de DFD0 y DFD1
- Esquema E/R del sistema
- Tablas del esquema E/R
- Dependencias funcionales, proceso de Normalización realizado y conjunto de tablas obtenido de dicho proceso, junto con las claves primarias y externas correspondientes.

> [!NOTE] 
Caja negra: Se concibe el SI como un solo proceso, conectado con todos los agentes externos y flujos de datos

> [!NOTE] 
Esquema armazón o DFD0: Cada subsistema representado como un sólo proceso, con flujos de datos con la/s base/s de datos

> [!IMPORTANT] 
Se hacen de más distendido a menos (DFD1, DFD0 y caja negra)

> [!WARNING]
Comprobar que no haya almacenes que ponga BD y arreglar diagrama usuarios para que no se superpongan las flechas de los flujos
### Primera parte
- [X] Caja negra
- [X] Armazón
- [X] DFD1
    - [X] Publicaciones
    - [X] Tendecias
    - [X] Publicidad
    - [X] Usuarios
    - [X] Mensajería
### Segunda parte
- [ ] Paso a tabla
    - [ ] Publicaciones
    - [ ] Tendecias
    - [ ] Publicidad
    - [ ] Usuarios
    - [ ] Mensajería
- [ ] Identificar las dependencias funcionales
    - [ ] Publicaciones
    - [ ] Tendecias
    - [ ] Publicidad
    - [ ] Usuarios
    - [ ] Mensajería
- [ ] Aplicar normalización del tema 3
    - [ ] Publicaciones
    - [ ] Tendecias
    - [ ] Publicidad
    - [ ] Usuarios
    - [ ] Mensajería


## Práctica 3 :gear:

Este repositorio contiene el código fuente y la documentación para la Práctica 3 de la asignatura **Diseño y Desarrollo de Sistemas de Información**.

El sistema implementa una arquitectura **Cliente-Servidor (2 capas)** utilizando **Python** para la interfaz/lógica de cliente y **Oracle PL/SQL** para la lógica de negocio y persistencia.

---

### 📂 Estructura del Proyecto

Para mantener el orden y evitar conflictos en Git, seguimos una **Arquitectura Modular Estricta**. Todo el código fuente de la Práctica 3 se encuentra bajo la carpeta `pr3/`.

```text
pr3/
requirements.txt <-- las librerías necesarias para el fichero py
├── database/                 <-- SCRIPTS SQL (Triggers, Procedures, DDL)
│   ├── 00_init_tablas.sql    <-- Script maestro de creación de tablas (Global)
│   ├── publicidad/           <-- Espacio de Ismael
│   ├── usuarios/             <-- Espacio de Fer
│   ├── publicaciones/        <-- Espacio de Javi
│   ├── tendencias/           <-- Espacio de Jesús
│   └── mensajeria/           <-- Espacio de Sergio
│
└── src/                      <-- CÓDIGO FUENTE PYTHON
    ├── main.py               <-- Punto de entrada (Gestionado por Ismael)
    ├── db_connection.py      <-- Conexión Singleton (Gestionado por Ismael)
    ├── publicidad/           <-- Módulo de Ismael
    ├── usuarios/             <-- Módulo de Fer
    ├── publicaciones/        <-- Módulo de Javi
    ├── tendencias/           <-- Módulo de Jesús
    └── mensajeria/           <-- Módulo de Sergio

```

---

### Uso de requirements.txt

El fichero `requirements.txt` sirve para decirle a tus compañeros (y al profesor) qué librerías externas necesitan instalar para que el código funcione en sus ordenadores.

En vuestro caso, como estáis usando una librería para conectaros a Oracle (`pyodbc` o `cx_Oracle`) y quizás alguna para mejorar la interfaz, es obligatorio tener este fichero. Sin él, cuando Fer o Javi se bajen tu código e intenten ejecutarlo, les dará el error: `ModuleNotFoundError`.

#### ¿Qué debéis poner dentro?

Dado el script del Seminario 1 y la estructura que os he pasado, cread el fichero `pr3/requirements.txt` y escribid esto dentro:

```text
# Driver ODBC para conectar con Oracle (Vital para la práctica)
pyodbc>=5.0.0

# (Opcional) Si queréis menús bonitos con colores como en el ejemplo
# colorama
# rich

```

#### ¿Cómo se usa?

1. **Para instalar todo de golpe:**
    Cuando un compañero se baja el proyecto, solo tiene que ejecutar:
    ```bash
    pip install -r requirements.txt

    ```


    Esto instalará `pyodbc` y cualquier otra cosa que añadáis, asegurando que todos tenéis la misma versión.

2. **Para generarlo automáticamente:**
    Si tú (Ismael) instalas una librería nueva (ej. `pip install pandas`), debes actualizar el fichero para que los demás lo sepan. Ejecuta:
    ```bash
    pip freeze > requirements.txt

    ```


Esto guarda todas las librerías que tienes instaladas en ese fichero.

### ⚠️ Reglas de Colaboración (LEER ANTES DE TOCAR)

Estamos trabajando todos en la misma rama. Para no romper el código de los demás, **se deben cumplir estas reglas sagradas**:

#### 1. Asignación de Archivos

* **Ismael:** Es el único autorizado para modificar archivos globales (`src/main.py`, `src/db_connection.py`, `requirements.txt`). También gestiona su módulo (`publicidad`).
* **Resto del Equipo (Fer, Javi, Jesús, Sergio):**
* SÓLO podéis editar archivos dentro de vuestras carpetas asignadas en `src/` y `database/`.
* **PROHIBIDO** editar `main.py`. Si necesitáis añadir vuestro menú al inicio, avisad a Ismael o pasadle el snippet de código.
* **PROHIBIDO** editar el código dentro de la carpeta de otro compañero.



#### 2. Flujo de Trabajo en Git

Al trabajar en una sola rama, la sincronización es clave:

1. **Antes de empezar a programar:** Ejecuta siempre `git pull` para bajarte los últimos cambios.
2. **Al terminar:** Haz `git add`, `git commit` y `git push` lo antes posible.
3. **Conflictos:** Si tocas solo tu carpeta, no debería haber conflictos. Si aparecen, lee con cuidado antes de aceptar cambios.

---

### Instalación y Ejecución

#### 1. Prerrequisitos

* Tener instalado Python 3.x.
* Tener instalado el **Oracle Instant Client** y los drivers ODBC configurados en tu sistema.
* Estar conectado a la VPN de la UGR (si estás fuera de la facultad).

#### 2. Configuración del Entorno

Es recomendable usar un entorno virtual para no ensuciar tu sistema:

```bash
# Crear entorno virtual (solo la primera vez)
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar librerías necesarias
pip install -r pr3/requirements.txt

```

#### 3. Ejecutar el Sistema

Sitúate en la carpeta `pr3/src/` y ejecuta el archivo principal:

```bash
cd pr3/src
python main.py

```

---

### 🛠 Guía de Desarrollo para el Equipo

#### ¿Cómo creo mi parte?

1. Ve a tu carpeta en `pr3/src/TU_MODULO/`.
2. Crea/Edita el archivo `menu.py`.
3. Copia la estructura básica:

```python
# Ejemplo de estructura para tu menu.py
def mostrar_menu(conn):
    while True:
        print("\n--- MI SUBSISTEMA ---")
        print("1. Opción A")
        print("0. Volver")
        # ... lógica ...

```

> A continuación, las funciones se definen en el fichero functions.py de cada subsistema.

#### ¿Cómo subo mis Triggers/Procedimientos?

1. Guarda tus scripts `.sql` en `pr3/database/TU_MODULO/`.
2. No los ejecutes solo en tu SQL Developer local; súbelos al Git para que el profesor vea el código PL/SQL entregado.

---



