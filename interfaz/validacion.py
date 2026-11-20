def validar_numero(texto, nombre, minimo, maximo):
    texto = texto.strip().replace(",", ".")

    if texto == "":
        raise ValueError(f"{nombre}: el campo está vacío.")

    try:
        valor = float(texto)
    except ValueError:
        raise ValueError(f"{nombre}: '{texto}' no es un número.")

    if not minimo <= valor <= maximo:
        raise ValueError(f"{nombre}: debe estar entre {minimo:g} y {maximo:g}.")

    return valor
