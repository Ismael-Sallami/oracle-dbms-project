CREATE OR REPLACE PROCEDURE CONTRATAR_ANUNCIO (
    p_idanuncio      IN VARCHAR2,
    p_titulo         IN VARCHAR2,
    p_cuerpo         IN VARCHAR2,
    p_enlace         IN VARCHAR2,
    p_fechafin       IN DATE,
    p_nom_carac      IN VARCHAR2, 
    p_val_carac      IN VARCHAR2,
    p_id_propietario IN NUMBER    
) AS
BEGIN
    -- 1. Insertar Anuncio
    INSERT INTO ANUNCIO (IDANUNCIO, TITULO, CUERPO, ENLACE, FECHAFIN, ESTADO, IDPROPIETARIO)
    VALUES (p_idanuncio, p_titulo, p_cuerpo, p_enlace, p_fechafin, 'ACTIVO', p_id_propietario);

    -- 2. Insertar Característica (El Trigger saltará aquí si hay error)
    IF p_nom_carac IS NOT NULL AND p_val_carac IS NOT NULL THEN
        INSERT INTO CARACTERISTICA (IDANUNCIO, NOMBRE, VALOR)
        VALUES (p_idanuncio, p_nom_carac, p_val_carac);
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE; 
END;
/