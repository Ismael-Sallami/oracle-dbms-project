from .functions import(
    crear_publicacion,
    modificar_publicacion,
    listar_publicaciones,
    eliminar_publicacion
)
from .utils import conversion_a_int_seguro, confirmar_resultado, input_truncado

def obtener_id_publicacion(cursor,id_usuario):
    id_publicacion=input("Introduzca el id de publicación (Deje vacío para listar sus publicaciones)")
    id_publicacion=conversion_a_int_seguro(id_publicacion,default=-1)

    """
    si el usuario no sabe el id_publicación (bastante razonable), se le lista sus publicaciones
    con el id_usuario, vamos a ser majos y no le vamos a poner anuncios por estar
    viendo sus propias publicaciones... debido a ello, la conexión puede ser None
    ya que esta conexión era para el subsistema de anuncios
    """
    while id_publicacion == -1:
        """
        Conexion es None, como solo necesitamos la conexion para los anuncios
        en caso de búsqueda privada (como es este caso), el que se comparta o no
        la conexion implica si queremos que haya anuncios o no, en este caso, como
        no hay anuncios, no pasamos ninguna conexión, aún así, si quisiéramos
        poner anuncios en un futuro sería tan fácil como añadir un argumento a esta función
        y pasarlo a listar publicaciones. Pero esa NO es la intención ahora y posiblemente nunca
        """
        print("A continuación se listan sus publicaciones, copie el id_publicacion de la publicación que quiera modificar, aparece debajo del título")
        listar_publicaciones(cursor,id_usuario)
        id_publicacion = input("¿Ha podido guardar correctamente la id? Péguelo en este prompt (déjelo vacío si desea volver a intentarlo o abandonar la operación)")
        id_publicacion=conversion_a_int_seguro(id_publicacion,default=-1)

        if id_publicacion == -1:
            print("Puede volver a listar las publicaciones o dejar la operación")
            resultado = confirmar_resultado("¿Desea volver a listar las publicaciones?[y/n]")
            if resultado == "n":
                print("Entendido, abortando...")
                id_publicacion = None

    return id_publicacion


def menu_edicion():
    """
    Pequeña interfaz para la edición de datos
    Si el valor es un string vacío, se conserva el valor
    original.
    Si el valor es None, se borra la descripción original (se queda en null).
    Excepto para el nombre (que no puede ser null).
    Se devolverá None (null) si se cancelan los cambios
    """
    nombre=""
    descripcion=""
    imagen=""
    categoria=""
    while True:
        print("\n========================================")
        print(" MENÚ PUBLICACIONES - EDITAR PUBLICACION ")
        print("========================================")
        print(f"1. Editar nombre" + (f": ({nombre})" if nombre else ""))
        print(f"2. Editar descripción" + (f": ({descripcion})" if descripcion else ""))
        print(f"3. Editar imagen" + (f": ({imagen})" if imagen else ""))
        print(f"4. Editar categoría" + (f": ({categoria})" if categoria else ""))
        print("5. Realizar cambios")
        print("6. Cancelar cambios y volver")
        print("----------------------------------------")
        
        opcion=input("Seleccione una opción: ").strip()
        opcion=conversion_a_int_seguro(opcion)

        if opcion == 1:
            print("Recordatorio: Si no introduce nada, no se cambiará el nombre")
            nombre = input_truncado("Nuevo nombre de publicación (20 caracteres): ", 20)
        elif opcion == 2:
            descripcion = input_truncado("Nueva descripcion de publicación (80 caracteres): ", 80)
            if not descripcion:
                print("Aviso: No se ha introducido ninguna descripción.")
                resultado = confirmar_resultado("¿Desea borrar la descripción? [y/n]")
                if resultado == "y":
                    descripcion = None 
        elif opcion == 3:
            imagen = input_truncado("Nueva imagen de la publicación (255 caracteres)", 255)
            if not imagen:
                print("Aviso: No se ha introducido ninguna imagen.")
                resultado = confirmar_resultado("¿Desea borrar la imagen? [y/n]")
                if resultado == "y":
                    imagen = None
        elif opcion == 4:
            categoria = input_truncado("Nueva categoría de la publicación (32 caracteres)", 32)
            if not categoria:
                print("Aviso: No se ha introducido ninguan categoría")
                resultado = confirmar_resultado("¿Desea borrar la categoría? [y/n]")
                if resultado == "y":
                    categoria = None
        elif opcion == 5:
            opciones = (nombre,descripcion,imagen,categoria)
            #no hay ningún cambio registrado
            if not any(no_vacio for no_vacio in opciones if no_vacio):
                print("Aviso: No se ha registrado ningún cambio, cancelando...")
                return None
            else:
                return (nombre,descripcion,imagen,categoria)
        elif opcion == 6:
            #Se cancela la edición
            return None 
        else:
            print(f"Opcion {opcion} inválida.")


def mostrar_menu_publicaciones(conexion, id_usuario):
    """
    Interfaz de usuario para el subsistema de Publicaciones.
    Recibe la conexión global compartida por el sistema.
    """
    cursor = conexion.cursor()
    
    while True:
        print("\n========================================")
        print("    SISTEMA EKIS - MENÚ PUBLICACIONES    ")
        print("========================================")
        print("1. Crear publicación (RF1.1)")
        print("2. Modificar publicación (RF1.2)")
        print("3. Listar publicaciones (RF1.3)")
        #print("4. Dar me gusta a publicacion (RF1.4)")
        print("4. Eliminar publicación (RF1.5)")
        print("5. Volver al Menú Principal")
        print("----------------------------------------")
        
        # El RF1.4: No se incluye porque se activa con un disparador.
        opcion=input("Seleccione una opción: ").strip()
        opcion=conversion_a_int_seguro(opcion)

        
        if opcion == 1:
            nombre = input_truncado("Introduzca nombre de la publicacion (20 caracteres máximo): ",20)
            while not nombre.strip():
                nombre = input_truncado("El nombre es obligatorio",20)
            imagen = input_truncado("Introduzca una imagen (opcional, 255): ",255)
            descripcion = input_truncado("Introduzca una descripción (opcional 80 caracteres máximo): ",80)
            categoria = input_truncado("Introduzca una categoria (opcional 32 caracteres máximo): ",32)

            if crear_publicacion(cursor, id_usuario, nombre, imagen, descripcion, categoria):
                conexion.commit()
                print("Se ha creado la publicación correctamente")
            else:
                print("Error en la creación de la publicación " + nombre)
            
            #Debido a que no se ve la publicación creada directamente,
            #cosa que seria recomendable cambiar, no hace falta eliminar el cursor
        elif opcion == 2:
            cambios = menu_edicion()
            #Hay que tener en cuenta si se ha cancelado la edición, en cuyo caso no se hace nada
            if not cambios:
                continue
            #Si hemos llegado hasta aquí entonces hay cambios por realizar, en ese caso, le damos
            #la opción al usuario de poner el id_publicación directamente. Si no conoce la id
            #se le da la opción de listar todas sus publicaciones y que copia un id_publicacion
            #en el caso en el que quiera cancelar la operación, devolverá None
            id_publicacion=obtener_id_publicacion(cursor,id_usuario)
            
            if id_publicacion and modificar_publicacion(cursor, id_usuario, id_publicacion, *cambios):
                conexion.commit()
                print("Se ha modificado la publicación correctamente")
            elif id_publicacion is not None:
                print("Error en la modificación de la publicación.")
            #Debido a que no se ve la publicación modificada directamente,
            #cosa que seria recomendable cambiar, no hace falta eliminar el cursor
        elif opcion == 3:
            #Al igual que con la opción 2, esta parte no es específica del requisito funcional
            #Así que de momento no se implementa
            #listar_un_solo_usuario = confirmar_resultado("¿Quiere ver las publicaciones de un usuario en específico?[y/n]")
            #if listar_un_solo_usuario == "y":
            
            listar_publicaciones(cursor,id_usuario,conexion)
        elif opcion == 4:
            id_publicacion=obtener_id_publicacion(cursor,id_usuario)
            if id_publicacion and eliminar_publicacion(cursor,id_usuario,id_publicacion):
                conexion.commit()
                print("Se ha eliminado la publicación correctamente")
            elif id_publicacion is not None:
                print("Error en la eliminación de la publcación")

        #Dar me gusta es un trigger, por lo que no está como opción
        elif opcion == 5:
            print("Saliendo del subsistema de Publicaciones...")
            break
            
        else:
            print("Opción no válida. Intente de nuevo.")

    cursor.close()
