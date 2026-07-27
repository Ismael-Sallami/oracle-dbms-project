def conversion_a_int_seguro(valor,default=None,error_default=None):
    try:
        valor=int(valor) if valor else default
    except ValueError:
        print("Error, valor no válido como id")
        valor=error_default
    return valor

def confirmar_resultado(pregunta):
    while True:
        respuesta = input(pregunta).lower()
        if respuesta in ['y','n']:
            return respuesta
        print("Error. Responda con [y/n]")

#obtener valores truncados
def input_truncado(enunciado: str, MAX_CHARS: int):
    valor = input(enunciado)
    return valor[:MAX_CHARS]

#normalizar valores
def vacio_a_none(valor: str | None):
    if valor is None or valor.strip() == "":
        return None 
    return valor
