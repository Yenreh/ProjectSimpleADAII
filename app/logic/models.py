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
        Si e > 0, se asume que esos agentes son removidos.
        """
        if e > self.n:
            raise ValueError("No se pueden moderar más agentes de los que hay en el grupo.")
        return GrupoAgentes(self.n - e, self.op1, self.op2, self.rig)

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
        suma_conflicto = sum(grupo.conflicto_contribucion() for grupo in self.grupos)
        suma_agentes = sum(grupo.n for grupo in self.grupos)
        return suma_conflicto / suma_agentes if suma_agentes != 0 else 0

    def aplicar_estrategia(self, estrategia):
        """
        Aplica la estrategia de moderación a la red.
        estrategia: lista de enteros [e0, e1, ..., en-1].
        Devuelve una nueva instancia de RedSocial con los grupos actualizados.
        """
        nuevos_grupos = []
        for i in range(len(self.grupos)):
            nuevos_grupos.append(self.grupos[i].clonar_con_moderacion(estrategia[i]))
        return RedSocial(nuevos_grupos, self.R_max)

    def calcular_esfuerzo_total(self, estrategia):
        """
        Calcula el esfuerzo total de una estrategia.
        """
        esfuerzo_total = 0
        for i in range(len(self.grupos)):
            esfuerzo_total += self.grupos[i].calcular_esfuerzo(estrategia[i])
        return esfuerzo_total

    def generar_todas_las_estrategias(self):
        """
        Genera todas las combinaciones posibles de estrategias,
        sin usar itertools.
        """
        estrategias = [[]]
        for grupo in self.grupos:
            nuevas_estrategias = []
            for estrategia in estrategias:
                for e in range(grupo.n + 1):
                    nuevas_estrategias.append(estrategia + [e])
            estrategias = nuevas_estrategias
        return estrategias

    def modciFB(self):
        """
        Fuerza Bruta:
        Genera todas las estrategias, filtra las aplicables y retorna la que minimiza el conflicto.
        """
        estrategias_posibles = self.generar_todas_las_estrategias()
        mejor_conflicto, mejor_estrategia, mejor_esfuerzo = float('inf'), None, None
        for estrategia in estrategias_posibles:
            esfuerzo_total = self.calcular_esfuerzo_total(estrategia)
            if esfuerzo_total > self.R_max:
                continue
            red_mod = self.aplicar_estrategia(estrategia)
            conflicto_actual = red_mod.calcular_conflicto_interno()
            if conflicto_actual < mejor_conflicto:
                mejor_conflicto, mejor_estrategia, mejor_esfuerzo = conflicto_actual, estrategia, esfuerzo_total
        return mejor_estrategia, mejor_esfuerzo, mejor_conflicto

    def modciV(self):
        """
        Algoritmo Voraz (placeholder).
        Por el momento, se reutiliza la lógica de fuerza bruta.
        """
        return "Algoritmo Voraz no implementado", None, None

    def modciDP(self):
        """
        Programación Dinámica (placeholder).
        Por el momento, se reutiliza la lógica de fuerza bruta.
        """
        return "Programación Dinámica no implementada", None, None
