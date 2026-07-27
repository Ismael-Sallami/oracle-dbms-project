# Diseño

### 1. 🚨 Error Crítico: Diseño de Datos de Mensajería (Páginas 87 y 90)

Este es el punto más importante. El modelo relacional propuesto para la mensajería tiene fallos lógicos graves que impedirían el funcionamiento del sistema según los requisitos.

**El problema:**
En la tabla de la página 87 (Paso a Tabla) y la justificación de normalización en la página 90:
* **Tabla 11 `ENVIA`:** Definís `idUsuario1` como **CP (Clave Primaria)** y `idUsuario2` como **CC (Clave Candidata)**.
    * *Consecuencia:* Al ser `idUsuario1` la CP, un usuario **solo podría aparecer una vez** en esa tabla. Es decir, un usuario solo podría enviar un mensaje (o tener una conversación) en toda su vida en la red social. Además, al ser `idUsuario2` clave candidata (única), un usuario solo podría recibir un mensaje de una sola persona.
    * *Violación de Requisito:* Esto viola el RF5.1 que permite enviar múltiples mensajes.

* **Tabla 12 `CONTIENE`:** Relaciona `idUsuario` con `idMensaje`, donde `idMensaje` es la CP.
    * *Consecuencia:* Un mensaje solo puede estar relacionado con **un** usuario. ¿Quién es ese usuario? ¿El emisor o el receptor? Un mensaje necesita estar vinculado a ambos.

**La Solución Sugerida:**
La forma estándar de modelar esto (y que cumple FNBC) es simplificarlo eliminando las tablas 11 y 12, e integrando las claves foráneas en la tabla Mensaje:

* **Tabla `MENSAJE`:**
    * `idMensaje` (CP)
    * `idEmisor` (CF hacia Usuario)
    * `idReceptor` (CF hacia Usuario)
    * `mensaje`
    * `fechaEnvio`
    * `horaEnvio`
    * `bitVisto`

Si queréis mantener la tabla `ENVIA` para representar "Conversaciones activas" (no mensajes individuales), la Clave Primaria debería ser compuesta `(idUsuario1, idUsuario2)`.

---

### 2. Inconsistencias en Requisitos vs. Datos

He encontrado discrepancias entre lo que piden los Requisitos Funcionales (RF) y lo que aparece en las tablas finales:

* **El atributo "Likes" (Pág. 14 vs Pág. 87):**
    * En *RDW1.1* (Pág. 14), definís `Likes` como un **Entero**. Esto sugiere que guardáis el contador total en la tabla de la publicación.
    * En la Tabla 7 (Pág. 87), creáis correctamente la tabla `LIKE (idUsuario, idPublicacion)`.
    * *Observación:* Si tenéis la tabla 7, el atributo "Entero" en la tabla `PUBLICACION` es un dato **derivado/calculado** (redundante). En bases de datos estrictamente normalizadas, no se suele guardar el contador si ya tienes la tabla de relaciones, a menos que justifiquéis que es por rendimiento (desnormalización controlada).
    * *Sugerencia:* Aclarad si el atributo "Likes" en `PUBLICACION` es un campo calculado o eliminadlo del esquema relacional para ser puristas con la normalización.

* **Nombres de Atributos (Typo):**
    * En los requisitos (Pág. 46), lo llamáis **"Bit de visualización"**.
    * En la Tabla 5 (Pág. 87), lo llamáis **"bitAviso"**.
    * *Sugerencia:* Unificad el nombre (ej. `bitVisto` o `leido`).

* **RF1.3 Listar Publicaciones (Pág. 17):**
    * El requisito dice: *"Una de cada 5 publicaciones tendrá un anuncio"*.
    * En el esquema (Pág. 87), tenéis la tabla `CONTIENE_PUBLICIDAD`.
    * *Observación:* La restricción de "1 de cada 5" es lógica de negocio (código), no de base de datos. La tabla `CONTIENE_PUBLICIDAD` está bien modelada (1:1 o 1:N), pero aseguraos de que el diagrama ER refleje que una publicación puede tener **0 o 1** anuncio (cardinalidad 0..1), lo cual parece correcto en vuestro diagrama de la pág 72.

---

### 3. Erratas en los Diagramas (Esquema Externo)

* **Página 82 (Diagrama de Bloquear/Añadir Amigo):**
    * La relación `BloquearUsuario` y `AñadirAmigo` tiene cardinalidades `0..n` en un lado y `0..m` en el otro.
    * Sin embargo, en la Tabla 9 y 10 (Pág. 87), la clave primaria es compuesta `(idUsuario1, idUsuario2)`. Esto es correcto para una relación N:M.
    * *Nota:* Aseguraos de que vuestro diagrama ER (Pág. 82) use la notación correcta para relaciones recursivas. La notación actual es un poco ambigua sobre si es simétrica o no, pero el paso a tablas lo habéis resuelto bien (excepto por el tema de la mensajería mencionado arriba).

---

### 4. Normalización (Página 90)

En la sección **"Casos Específicos de Cardinalidad Restringida"**, defendéis la Tabla 11 `ENVIA`:

> "Se define idUsuario1 como Clave Primaria (PK) e idUsuario2 como Clave Candidata (CC)."

Esto confirma el error del punto 1. Al justificar la normalización FNBC basándoos en esta definición de claves, estáis validando matemáticamente un diseño que **funcionalmente es incorrecto** (un usuario solo puede enviar un mensaje).
* Si corregís el diseño (haciendo que `Mensaje` tenga emisor/receptor), tendréis que reescribir esta justificación de normalización para la tabla `MENSAJE`.

### Resumen de pasos siguientes para vosotros:

1.  **Modificar la Tabla 5 (MENSAJE):** Añadir `idEmisor` y `idReceptor` como claves foráneas.
2.  **Eliminar las Tablas 11 (ENVIA) y 12 (CONTIENE):** Son redundantes e incorrectas tal como están planteadas.
3.  **Corregir la justificación de Normalización (Pág. 90):** Adaptarla a la nueva estructura de `MENSAJE`.
4.  **Unificar nomenclatura:** Decidir entre `bitAviso` o `bitVisto`.

¿Te gustaría que te ayude a redactar la justificación de la normalización corregida para la tabla de Mensajes?



[cite_start]Para corregir el diseño de la mensajería mencionado en el punto 1, ambas claves foráneas (`idEmisor` y `idReceptor`) deben apuntar hacia la tabla **`USUARIO`** (Tabla 1 del documento)[cite: 1149].

Aquí tienes el detalle técnico de cómo quedarían esas referencias:

* **`idEmisor` (Clave Foránea):** Apunta a la tabla **`USUARIO`** (al campo `idUsuario`). Identifica quién envió el mensaje.
* **`idReceptor` (Clave Foránea):** Apunta **también** a la tabla **`USUARIO`** (al campo `idUsuario`). Identifica quién recibe el mensaje.

**Esquema resultante para la tabla MENSAJE:**

| Atributo | Tipo de Clave | Referencia (Hacia dónde apunta) |
| :--- | :--- | :--- |
| `idMensaje` | **CP** (Clave Primaria) | N/A |
| `idEmisor` | **CF** (Clave Foránea) | Tabla **`USUARIO`** (`idUsuario`) |
| `idReceptor` | **CF** (Clave Foránea) | Tabla **`USUARIO`** (`idUsuario`) |
| `mensaje` | | |
| `fechaEnvio` | | |
| ... | | |

[cite_start]Al apuntar ambas claves a la misma tabla (`USUARIO`), permites que cualquier usuario registrado pueda actuar tanto como emisor como receptor, resolviendo el problema lógico que tenías en el diseño original donde separabas la relación en tablas diferentes (`ENVIA` y `CONTIENE`)[cite: 1149].



- Corregir lo de las claves candidatas de que email y telefono puede ser.