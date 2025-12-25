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