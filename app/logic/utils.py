from app.logic.models import GrupoAgentes, RedSocial

def parsear_entrada(texto):
    """
    Parsea el contenido del archivo de entrada.
    Formato esperado:
      Línea 1: número de grupos (n)
      Líneas 2 a n+1: cada línea con "n, op1, op2, rig" separados por comas.
      Última línea: R_max.
    Retorna una instancia de RedSocial.
    """
    lineas = [linea.strip() for linea in texto.strip().splitlines() if linea.strip()]
    num_grupos = int(lineas[0])
    grupos = []
    for i in range(1, num_grupos + 1):
        partes = lineas[i].split(',')
        n = int(partes[0].strip())
        op1 = int(partes[1].strip())
        op2 = int(partes[2].strip())
        rig = float(partes[3].strip())
        grupos.append(GrupoAgentes(n, op1, op2, rig))
    R_max = int(lineas[num_grupos + 1].strip())
    return RedSocial(grupos, R_max, num_grupos)

def formatear_salida(red, estrategia, esfuerzo, conflicto):
    """
    Formatea la salida de un algoritmo.
    Formato:
      Línea 1: CI
      Línea 2: Esfuerzo total
      Línea 3 en adelante: número de agentes moderados en cada grupo.
    """
    salida = [str(conflicto), str(esfuerzo)] + [str(e) for e in estrategia]
    return "\n".join(salida)
