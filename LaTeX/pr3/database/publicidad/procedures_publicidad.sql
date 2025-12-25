CREATE OR REPLACE PROCEDURE CONTRATAR_ANUNCIO (
    p_idanuncio   IN VARCHAR2,
    p_titulo      IN VARCHAR2,
    p_cuerpo      IN VARCHAR2,
    p_enlace      IN VARCHAR2,
    p_fechafin    IN DATE,
    p_nom_carac   IN VARCHAR2, 
    p_val_carac   IN VARCHAR2  
) AS
BEGIN
    INSERT INTO ANUNCIO (
        IDANUNCIO, TITULO, CUERPO, ENLACE, FECHAFIN, 
        NOMBRECARACTERISTICA, VALORCARACTERISTICA
    )
    VALUES (
        p_idanuncio, p_titulo, p_cuerpo, p_enlace, p_fechafin,
        p_nom_carac, p_val_carac
    );

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/