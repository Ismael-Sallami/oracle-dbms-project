/* =========================================================
PROCEDIMIENTO: CONTRATAR_ANUNCIO
Realiza la transacción de inserción. Simula el cobro.
========================================================= */
CREATE OR REPLACE PROCEDURE CONTRATAR_ANUNCIO (
    p_idanuncio   IN VARCHAR2,
    p_titulo      IN VARCHAR2,
    p_cuerpo      IN VARCHAR2,
    p_enlace      IN VARCHAR2,
    p_fechafin    IN DATE
) AS
    v_coste_simulado NUMBER := 50; -- Simulamos que cuesta 50€
BEGIN
    -- 1. Aquí iría la lógica de comprobar saldo del usuario (Simulada)
    -- DBMS_OUTPUT.PUT_LINE('Cobrando ' || v_coste_simulado || '€ al usuario...');

    -- 2. Insertar el anuncio
    -- Nota: Al usar la tabla simple de APEX, no insertamos ID_USUARIO ni PRESUPUESTO
    INSERT INTO ANUNCIO (IDANUNCIO, TITULO, CUERPO, ENLACE, FECHAFIN)
    VALUES (p_idanuncio, p_titulo, p_cuerpo, p_enlace, p_fechafin);

    -- 3. Confirmar transacción
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK; -- Si algo falla, deshacemos todo
        RAISE;    -- Y lanzamos el error a Python
END;
/