import math
import itertools

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
        nuevo_n = self.n - e if e > 0 else self.n
        # Se mantiene op1, op2 y rig, ya que la moderación implica que los moderados ya no se consideran.
        return GrupoAgentes(nuevo_n, self.op1, self.op2, self.rig)

class RedSocial:
    def __init__(self, grupos, R_max):
        """
        Inicializa una red social.
        grupos: lista de instancias de GrupoAgentes
        R_max: esfuerzo máximo disponible para moderar opiniones.
        """
        self.grupos = grupos
        self.R_max = R_max

    def calcular_conflicto_interno(self):
        """
        Calcula el conflicto interno de la red social usando la fórmula:
        CI = (∑ [n_i * (op1_i - op2_i)^2]) / (∑ [n_i])
        """
        suma_conflicto = sum(g.conflicto_contribucion() for g in self.grupos)
        suma_agentes = sum(g.n for g in self.grupos)
        return suma_conflicto / suma_agentes if suma_agentes != 0 else 0

    def aplicar_estrategia(self, estrategia):
        """
        Aplica la estrategia de moderación a la red.
        estrategia: lista de enteros [e0, e1, ..., en-1] donde cada e indica
                    el número de agentes a moderar en el grupo correspondiente.
        Devuelve una nueva instancia de RedSocial con los grupos actualizados.
        """
        if len(estrategia) != len(self.grupos):
            raise ValueError("La estrategia debe tener el mismo número de elementos que grupos.")
        nuevos_grupos = []
        for grupo, e in zip(self.grupos, estrategia):
            nuevos_grupos.append(grupo.clonar_con_moderacion(e))
        return RedSocial(nuevos_grupos, self.R_max)

    def calcular_esfuerzo_total(self, estrategia):
        """
        Calcula el esfuerzo total de una estrategia.
        Suma el esfuerzo de cada grupo usando su método calcular_esfuerzo.
        """
        return sum(grupo.calcular_esfuerzo(e) for grupo, e in zip(self.grupos, estrategia))

    def modciFB(self):
        """
        Resuelve el problema usando fuerza bruta:
        - Genera todas las estrategias posibles.
        - Filtra las que son aplicables (esfuerzo_total <= R_max).
        - Calcula el conflicto interno resultante para cada estrategia.
        - Retorna la estrategia que minimiza el conflicto interno,
          junto con su esfuerzo total y el conflicto resultante.
        """
        rangos = [range(grupo.n + 1) for grupo in self.grupos]
        mejor_conflicto = float('inf')
        mejor_estrategia = None
        mejor_esfuerzo = None

        for estrategia in itertools.product(*rangos):
            esfuerzo_total = self.calcular_esfuerzo_total(estrategia)
            if esfuerzo_total > self.R_max:
                continue  # Estrategia no aplicable
            red_mod = self.aplicar_estrategia(estrategia)
            conflicto_actual = red_mod.calcular_conflicto_interno()
            if conflicto_actual < mejor_conflicto:
                mejor_conflicto = conflicto_actual
                mejor_estrategia = estrategia
                mejor_esfuerzo = esfuerzo_total

        return mejor_estrategia, mejor_esfuerzo, mejor_conflicto

    def modciV(self):
        """
        Algoritmo Voraz que unifica el cálculo de costos con el resto:
        1) Selecciona el grupo con mejor 'beneficio/costo_incr' en cada paso.
        2) Calcula el costo incremental real al pasar de e_i a e_i+1.
        3) Si cabe en el presupuesto, se modera un agente más.
        4) Al final, se calcula el costo total con la fórmula unificada.
        """

        n = len(self.grupos)
        # Inicializamos la estrategia: ningún agente moderado al inicio
        estrategia = [0] * n

        # Presupuesto gastado acumulado (calculado incrementalmente)
        presupuesto_usado = 0

        # Precalcular la diferencia d[i] = |op1 - op2| para cada grupo
        diferencias = [abs(g.op1 - g.op2) for g in self.grupos]

        # Mientras se pueda moderar (iteramos hasta que no haya mejora posible)
        while True:
            mejor_ratio = -1
            mejor_indice = None
            incremento_costo = 0

            for i, grupo in enumerate(self.grupos):
                if estrategia[i] < grupo.n:
                    # Costo actual si tenemos e_i agentes moderados
                    costo_actual = grupo.calcular_esfuerzo(estrategia[i])
                    # Costo si moderamos un agente más
                    costo_siguiente = grupo.calcular_esfuerzo(estrategia[i] + 1)
                    # Incremento real
                    delta = costo_siguiente - costo_actual

                    if delta <= 0:
                        # Teóricamente podría pasar si rig=0, etc.
                        # Evitar confusiones y forzar delta >= 1
                        delta = 1

                    if presupuesto_usado + delta <= self.R_max:
                        # Beneficio = reducción en conflicto al moderar 1 agente más
                        beneficio = (diferencias[i] ** 2)
                        ratio = beneficio / delta
                        if ratio > mejor_ratio:
                            mejor_ratio = ratio
                            mejor_indice = i
                            incremento_costo = delta

            if mejor_indice is None:
                # No se puede moderar más a nadie sin pasar el presupuesto
                break

            # Moderamos un agente en mejor_indice
            estrategia[mejor_indice] += 1
            presupuesto_usado += incremento_costo

        # Una vez terminada la selección, calculamos el costo total unificado
        costo_total = self.calcular_esfuerzo_total(estrategia)

        # Calcular el conflicto interno de la red resultante
        conflicto_total = 0
        total_agentes = 0
        for i, grupo in enumerate(self.grupos):
            agentes_restantes = grupo.n - estrategia[i]
            conflicto_total += agentes_restantes * (diferencias[i] ** 2)
            total_agentes += agentes_restantes

        valor_conflicto = conflicto_total / total_agentes if total_agentes > 0 else 0

        return estrategia, costo_total, valor_conflicto


    def modciDP(self):
        """
        Programación Dinámica (placeholder).
        Por el momento, se reutiliza la lógica de fuerza bruta.
        """
        return "Programación Dinámica no implementada", None, None

