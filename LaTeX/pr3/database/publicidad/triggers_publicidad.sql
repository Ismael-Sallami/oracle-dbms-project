/* =========================================================
TRIGGER 1: Validación de Coherencia Temporal (Adaptado)
========================================================= */

CREATE OR REPLACE TRIGGER TRG_PUB_VALIDAR_FECHAS
BEFORE INSERT OR UPDATE ON ANUNCIO
FOR EACH ROW
BEGIN
    -- Al no tener FECHA_INICIO, validamos contra la fecha actual (SYSDATE).
    -- Regla: No se puede crear o modificar un anuncio para que termine en el pasado.

    -- TRUNC(SYSDATE) elimina la hora para comparar solo fechas (día/mes/año)
    IF :NEW.FECHAFIN < TRUNC(SYSDATE) THEN
        RAISE_APPLICATION_ERROR(-20001, 'Error de Negocio: La fecha de fin del anuncio no puede ser anterior a la fecha actual.');
    END IF;
END;
/

/* =========================================================
TRIGGER 2: Auditoría de Cambios en FECHAFIN
========================================================= */

CREATE OR REPLACE TRIGGER TRG_AUDITAR_CAMBIO_FECHA
AFTER UPDATE OF FECHAFIN ON ANUNCIO
FOR EACH ROW
BEGIN
    INSERT INTO HISTORIAL_CAMBIOS_FECHA (IDANUNCIO, FECHA_ANTIGUA, FECHA_NUEVA)
    VALUES (:OLD.IDANUNCIO, :OLD.FECHAFIN, :NEW.FECHAFIN);
END;
/

-- Puede servir para analizar tendencias, ya que si vemos que se suele extender anuncios de x tipo, podemos pensar que es por que es una tendencia.

/* =========================================================
TRIGGER 3: Comprobar característica
========================================================= */

CREATE OR REPLACE TRIGGER TRG_VALIDAR_COHERENCIA
BEFORE INSERT OR UPDATE ON CARACTERISTICA 
FOR EACH ROW
DECLARE
    v_nombre_norm VARCHAR2(100);
    v_valor_norm  VARCHAR2(100);
BEGIN
    -- 1. Normalizamos los datos (quitamos espacios y pasamos a mayúsculas)
    --    Esto evita errores tontos como ' Rojo ' o 'color'
    v_nombre_norm := UPPER(TRIM(:NEW.NOMBRE));
    v_valor_norm  := UPPER(TRIM(:NEW.VALOR));

    -- 2. Lógica de control (Switch case)
    CASE v_nombre_norm
        
        -- CASO 1: Validación de Colores
        WHEN 'COLOR' THEN
            -- Aquí definimos la lista blanca de colores permitidos
            IF v_valor_norm NOT IN ('ROJO', 'AZUL', 'VERDE', 'AMARILLO', 'NEGRO', 'BLANCO', 'GRIS') THEN
                RAISE_APPLICATION_ERROR(-20005, 
                    'Valor incoherente: "' || :NEW.VALOR || '" no es un color válido. Use: Rojo, Azul, Verde, etc.');
            END IF;

        -- CASO 2: Validación de Tamaño (Ejemplo extra)
        WHEN 'TAMANO' THEN
            IF v_valor_norm NOT IN ('PEQUEÑO', 'MEDIANO', 'GRANDE', 'BANNER', 'FULLSCREEN') THEN
                RAISE_APPLICATION_ERROR(-20005, 
                    'Valor incoherente: "' || :NEW.VALOR || '" no es un tamaño válido.');
            END IF;

        -- CASO 3: Validación de Prioridad
        WHEN 'PRIORIDAD' THEN
            IF v_valor_norm NOT IN ('ALTA', 'MEDIA', 'BAJA') THEN
                RAISE_APPLICATION_ERROR(-20005, 'La prioridad solo puede ser Alta, Media o Baja.');
            END IF;

        -- Si el nombre es otra cosa (ej: "Material"), dejamos pasar cualquier valor
        ELSE
            NULL; 
            
    END CASE;

END;
/