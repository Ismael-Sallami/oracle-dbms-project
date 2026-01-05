# Guía TIKZ

## Guía de Estilos Personalizados TikZ para Diagramas de Diseño de Datos

Esta guía se basa en la representación de elementos definidos en la metodología de análisis y diseño conjunto:

*   **DFD:** Agentes externos (rectángulo), Procesos (rectángulo esquinas redondeadas o círculo), Almacenes de datos (rectángulo abierto), y Flujos de datos (flechas).
*   **E/R:** Entidades (rectángulo), Relaciones (diamante o línea, aquí usamos diamante por convención visual clara), y Atributos (elipse o dentro de la entidad). Los Esquemas Externos pueden representarse dentro de un contorno, idealmente un hexágono.

### 1. Configuración Inicial en \LaTeX

Antes de definir los estilos, es necesario incluir los paquetes necesarios, especialmente `tikz` y sus librerías esenciales para posicionamiento y formas.

```latex
\usepackage{tikz}
\usetikzlibrary{
    calc,           % Para cálculos de coordenadas
    positioning,    % Para colocar nodos de manera relativa (ej: below of)
    shapes,         % Para formas avanzadas (diamantes, elipses, etc.)
    arrows,         % Para estilos de flechas
    fit             % Para ajustar un nodo a un conjunto de nodos
}
```

### 2. Estilos Personalizados para Diagramas de Flujo de Datos (DFD)

Los estilos de DFD deben reflejar la simbología utilizada en el Diagrama de Caja Negra, DFD0 (Armazón) y DFD1 (por subsistema).

Se utiliza `\tikzstyle` o `\tikzset` para definir los estilos globales.

#### Definición de Estilos DFD

| Componente | Representación Metodológica | Estilo TikZ |
| :--- | :--- | :--- |
| **Agente Externo** | Rectángulo (No forma parte del SI) | `agente` |
| **Proceso** | Rectángulo con esquinas redondeadas | `proceso` |
| **Almacén de Datos (BD)** | Rectángulo abierto por la derecha | `almacen` |
| **Flujo de Datos** | Flecha etiquetada (RDE, RDW, RDR, RDS) | `flujo` |

```latex
\tikzstyle{agente} = [
    rectangle, draw, thick, 
    minimum width=2.5cm, minimum height=1cm, 
    fill=blue!15, text centered, 
    font=\bfseries\small
] % Agente Externo

\tikzstyle{proceso} = [
    rectangle, rounded corners=5pt, draw, thick, 
    minimum width=2.5cm, minimum height=1cm, 
    fill=green!20, text centered, 
    font=\bfseries\small
] % Proceso

\tikzstyle{almacen} = [
    rectangle, draw, thick, 
    minimum width=3cm, minimum height=1cm, 
    fill=yellow!20, 
    text centered, inner sep=5pt,
    font=\bfseries\small,
    % Comando para dibujar las líneas laterales que simulan el rectángulo abierto
    append after command={
        \pgfextra{
            \draw[thick] (\tikzlastnode.north west) -- (\tikzlastnode.south west);
            \draw[thick] (\tikzlastnode.north east) -- (\tikzlastnode.south east);
        }
    }
] % Almacén de datos (Base de Datos)

\tikzstyle{flujo} = [
    ->, very thick, >=stealth, 
    font=\small
] % Flujo de datos
```

#### Ejemplo de Uso DFD (Subsistema de Publicidad)

Este ejemplo muestra cómo el Administrador (Agente) interactúa con el proceso "Añadir Anuncio" (RF3.1), y cómo este proceso escribe en el Almacén de Datos (BD).

```latex
\begin{tikzpicture}[node distance=3cm, auto]

    % Nodos
    \node[agente] (Admin) {Administrador};
    \node[proceso, below of=Admin] (RF31) {RF3.1: Añadir Anuncio};
    \node[almacen, right of=RF31, node distance=4cm] (BD) {BD EKIS};

    % Flujos de datos (Etiquetados con RDE y RDW)
    \draw[flujo] (Admin) -- node[midway, left] {RDE3.1 (Datos Anuncio)} (RF31);
    \draw[flujo] (RF31) -- node[midway, above] {RDW3.1 (Escritura)} (BD);

\end{tikzpicture}
```

### 3. Estilos Personalizados para Diagramas Entidad-Relación (E/R)

Los diagramas E/R se utilizan para crear los Esquemas Externos (visión conceptual parcial de la BD) y el Modelo Conceptual completo (integración de esquemas).

Utilizaremos la notación de rectángulos para entidades y diamantes para relaciones, junto con elipses para atributos (una notación híbrida común).

#### Definición de Estilos E/R

| Componente | Representación Metodológica | Estilo TikZ |
| :--- | :--- | :--- |
| **Entidad** | Rectángulo | `entidad` |
| **Relación** | Diamante (Asociación) | `relacion` |
| **Atributo/Clave** | Elipse (para destacar atributos clave) | `atributo` |
| **Contenedor** | Hexágono o rectángulo ajustado para Esquema Externo | `contenedor_ee` |

```latex
\tikzstyle{entidad} = [
    rectangle, draw, very thick, 
    minimum height=1.0cm, 
    fill=red!20, text centered, 
    font=\bfseries\small
] % Entidad

\tikzstyle{relacion} = [
    diamond, draw, very thick, 
    aspect=2, minimum height=0.8cm, 
    fill=orange!30, text centered, 
    font=\bfseries\small
] % Relación

\tikzstyle{atributo} = [
    ellipse, draw, thick, 
    fill=gray!20, text centered, 
    font=\small, inner sep=3pt
] % Atributo

\tikzstyle{link} = [
    thick
] % Conexión simple

\tikzstyle{cardinalidad} = [
    font=\scriptsize
] % Para etiquetas de cardinalidad/multiplicidad
```

#### Ejemplo de Uso E/R (Esquema Externo de Anuncio y Característica)

Este ejemplo modela conceptualmente la relación entre `Anuncio` y `Característica` para definir el público objetivo (RF3.2).

```latex
\begin{tikzpicture}[node distance=3cm, auto]

    % 1. Definición de nodos de datos
    \node[entidad] (Anuncio) {Anuncio};
    \node[entidad, right of=Anuncio, node distance=5cm] (Caract) {Característica};

    % 2. Definición de la Relación
    \node[relacion, midway between=Anuncio and Caract] (Dirigido) {Dirigido A};

    % 3. Definición de Atributos Clave (usando elipse para énfasis)
    \node[atributo] (IDAnuncio) [above of=Anuncio, node distance=1.5cm] {ID Anuncio (PK)};
    \node[atributo] (NomCar) [above of=Caract, node distance=1.5cm] {Nombre Característica};

    % 4. Conexiones
    \draw[link] (Anuncio) -- (Dirigido) node[pos=0.1, cardinalidad] {1} node[pos=0.9, cardinalidad] {N};
    \draw[link] (Caract) -- (Dirigido) node[pos=0.1, cardinalidad] {1} node[pos=0.9, cardinalidad] {N};
    
    \draw[link] (Anuncio) -- (IDAnuncio);
    \draw[link] (Caract) -- (NomCar);

    % 5. Contenedor del Esquema Externo (Opcional, usando fit)
    \node[draw, fill=cyan!5, thick, fit=(Anuncio) (Caract) (Dirigido) (IDAnuncio) (NomCar), inner sep=15pt, label={[font=\bfseries]above:Esquema Externo: RF3.2}] (EE) {};

\end{tikzpicture}
```

### 4. Consejos Adicionales para la Metodología

1.  **Consistencia de Flujos:** En los DFD, asegúrese de que los flujos de datos sean coherentes en la jerarquía. El refinamiento de un proceso (DFD0 $\to$ DFD1) debe mantener los mismos flujos de datos con los agentes externos y almacenes del nivel superior.
2.  **Modelado de Restricciones:** Al crear los Esquemas Externos de Publicidad, recuerde que deben modelar los datos teniendo en cuenta las **restricciones semánticas (RS)** asociadas. Por ejemplo, la restricción RS3.2 ("La fecha de fin debe ser posterior a la fecha de inicio") se modela conceptualmente con la presencia de ambos atributos (`Fecha de Inicio`, `Fecha de Fin`) en la entidad `Anuncio`.
3.  **Diferencia Agente vs. Entidad:** Recuerde que un Agente Externo en un DFD (un rectángulo en su estilo `agente`) **NO** es una Entidad en un diagrama E/R. Los Esquemas Externos son descripciones de **DATOS**, no de acciones.