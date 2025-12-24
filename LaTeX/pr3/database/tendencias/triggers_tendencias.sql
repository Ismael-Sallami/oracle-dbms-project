CREATE OR REPLACE TRIGGER TRG_PROCESAR_HASHTAGS
AFTER INSERT ON PUBLICACION
FOR EACH ROW
DECLARE
    -- Variables para extraer los hashtags
    v_hashtag VARCHAR2(32);
    v_count   NUMBER;
    v_i       NUMBER := 1;
BEGIN
    -- 1. Buscamos todos los términos que empiecen por # en la descripción
    -- REGEXP_COUNT nos dice cuántos hashtags hay
    FOR i IN 1 .. REGEXP_COUNT(:NEW.DESCRIPCION, '#[[:alnum:]_]+') LOOP
        
        -- Extraemos el i-ésimo hashtag encontrado
        -- (Que empiecen por # y quedándonos con todos los caracteres alfanuméricos y los _)
        -- 1 -> buscar desde la primera posición
        -- i -> extraer el iésimo hashtag
        v_hashtag := REGEXP_SUBSTR(:NEW.DESCRIPCION, '#[[:alnum:]_]+', 1, i);

        -- Solo procesamos si el hashtag mide 32 o menos (según tu especificación)
        IF LENGTH(v_hashtag) <= 32 THEN
            
            -- RS2.2: ¿Existe ya en la tabla HASHTAG?
            SELECT COUNT(*) INTO v_count FROM HASHTAG WHERE HASHTAG = v_hashtag;

            IF v_count > 0 THEN
                -- Si existe, actualizamos menciones
                UPDATE HASHTAG 
                SET MENCIONES = MENCIONES + 1 
                WHERE HASHTAG = v_hashtag;
            ELSE
                -- Si no existe, lo creamos con 1 mención
                INSERT INTO HASHTAG (HASHTAG, MENCIONES) 
                VALUES (v_hashtag, 1);
            END IF;

            -- Registramos la relación en la tabla CONTIENE_HASHTAG (Tabla 13)
            -- Usamos :NEW.IDPUBLICACION que es el ID que se acaba de generar
            INSERT INTO CONTIENE_HASHTAG (IDPUBLICACION, HASHTAG)
            VALUES (:NEW.IDPUBLICACION, v_hashtag);
            
        END IF;
    END LOOP;
END;
/