import math

class GrupoAgentes:
    def __init__(self, n, op1, op2, rig):
        """
        Inicializa un grupo de agentes.
        n: número de agentes
        op1: opinión sobre la afirmación 1
        op2: opinión sobre la afirmación 2
        rig: nivel de rigidez (entre 0 y 1)
        """
        self.n = n
        self.op1 = op1
        self.op2 = op2
        self.rig = rig

    def calcular_esfuerzo(self, e):
        """
        Calcula el esfuerzo necesario para moderar 'e' agentes en este grupo.
        Se utiliza la fórmula: ceil(|op1 - op2| * rig * e)
        """
        return math.ceil(abs(self.op1 - self.op2) * self.rig * e)

    def conflicto_contribucion(self):
        """
        Calcula la contribución del grupo al conflicto interno,
        es decir: n * (op1 - op2)^2.
        """
        return self.n * ((self.op1 - self.op2) ** 2)
    
    def clonar_con_moderacion(self, e):
        """
        Crea una copia del grupo luego de aplicar la moderación de 'e' agentes.
        Si e > 0, se asume que esos agentes son removidos (por haber moderado sus opiniones).
        """
        if e > self.n:
            raise ValueError("No se pueden moderar más agentes de los que hay en el grupo.")
        # Si se moderan agentes, se reduce el número de agentes.
        nuevo_n = self.n - e if e > 0 else self.n
        return GrupoAgentes(nuevo_n, self.op1, self.op2, self.rig)

class RedSocial:
    def __init__(self, grupos, R_max):
        """
        Inicializa una red social.
        grupos: lista de instancias de GrupoAgentes.
        R_max: esfuerzo máximo disponible para moderar opiniones.
        """
        self.grupos = grupos
        self.R_max = R_max

    def calcular_conflicto_interno(self):
        """
        Calcula el conflicto interno de la red social usando la fórmula:
        CI = (∑ [n_i * (op1_i - op2_i)^2]) / (∑ [n_i])
        """
        suma_conflicto = 0
        suma_agentes = 0
        for grupo in self.grupos:
            suma_conflicto += grupo.conflicto_contribucion()
            suma_agentes += grupo.n
        return suma_conflicto / suma_agentes if suma_agentes != 0 else 0

    def aplicar_estrategia(self, estrategia):
        """
        Aplica la estrategia de moderación a la red.
        estrategia: lista de enteros [e0, e1, ..., en-1] donde cada e indica
                    el número de agentes a moderar en el grupo correspondiente.
        Devuelve una nueva instancia de RedSocial con los grupos actualizados.
        """
        nuevos_grupos = []
        for i in range(len(self.grupos)):
            nuevos_grupos.append(self.grupos[i].clonar_con_moderacion(estrategia[i]))
        return RedSocial(nuevos_grupos, self.R_max)

    def calcular_esfuerzo_total(self, estrategia):
        """
        Calcula el esfuerzo total de una estrategia.
        Suma el esfuerzo de cada grupo usando su método calcular_esfuerzo.
        """
        esfuerzo_total = 0
        for i in range(len(self.grupos)):
            esfuerzo_total += self.grupos[i].calcular_esfuerzo(estrategia[i])
        return esfuerzo_total

    def generar_todas_las_estrategias(self):
        """
        Genera manualmente todas las combinaciones posibles de estrategias,
        sin usar itertools.
        Para cada grupo, se consideran los valores de 0 hasta n (inclusive).
        """
        estrategias = [[]]
        for grupo in self.grupos:
            nuevas_estrategias = []
            # Para cada estrategia parcial ya generada, se agregan todas las posibles opciones para el grupo actual.
            for estrategia in estrategias:
                for e in range(grupo.n + 1):
                    nuevas_estrategias.append(estrategia + [e])
            estrategias = nuevas_estrategias
        return estrategias

    def modciFB(self):
        """
        Resuelve el problema usando fuerza bruta:
        - Genera todas las estrategias posibles.
        - Filtra las que son aplicables (esfuerzo_total <= R_max).
        - Calcula el conflicto interno resultante para cada estrategia.
        - Retorna la estrategia que minimiza el conflicto interno,
          junto con su esfuerzo total y el conflicto resultante.
        """
        estrategias_posibles = self.generar_todas_las_estrategias()
        
        mejor_conflicto = float('inf')
        mejor_estrategia = None
        mejor_esfuerzo = None

        # Recorremos cada estrategia posible
        for estrategia in estrategias_posibles:
            esfuerzo_total = self.calcular_esfuerzo_total(estrategia)
            # Se descarta la estrategia si el esfuerzo supera R_max
            if esfuerzo_total > self.R_max:
                continue  
            red_mod = self.aplicar_estrategia(estrategia)
            conflicto_actual = red_mod.calcular_conflicto_interno()
            # Se actualiza la mejor solución si el conflicto es menor
            if conflicto_actual < mejor_conflicto:
                mejor_conflicto = conflicto_actual
                mejor_estrategia = estrategia
                mejor_esfuerzo = esfuerzo_total

        return mejor_estrategia, mejor_esfuerzo, mejor_conflicto

# Ejemplo de uso
if __name__ == "__main__":
    grupos_RS1 = [
        GrupoAgentes(3, -100, 50, 0.5),
        GrupoAgentes(1, 100, 80, 0.1),
        GrupoAgentes(1, -10, 0, 0.5)
    ]
    R_max_RS1 = 80
    red_social = RedSocial(grupos_RS1, R_max_RS1)

    # Ejemplo 2:
    grupos_RS2 = [
        GrupoAgentes(3, -100, 100, 0.8),
        GrupoAgentes(2, 100, 80, 0.5),
        GrupoAgentes(4, -10, 10, 0.5)
    ]
    R_max_RS2 = 400
    red_social_2 = RedSocial(grupos_RS2, R_max_RS2)

    print("Ejemplo 1:")
    estrategia, esfuerzo, conflicto = red_social.modciFB()
    print("Estrategia óptima:", estrategia)
    print("Esfuerzo total:", esfuerzo)
    print("Conflicto interno:", conflicto)


    print("Ejemplo 2:")
    estrategia, esfuerzo, conflicto = red_social_2.modciFB()
    print("Estrategia óptima:", estrategia)
    print("Esfuerzo total:", esfuerzo)
    print("Conflicto interno:", conflicto)