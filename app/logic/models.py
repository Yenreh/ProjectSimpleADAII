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
    def __init__(self, grupos, R_max, num_grupos):
        """
        Inicializa una red social.
        grupos: lista de instancias de GrupoAgentes
        R_max: esfuerzo máximo disponible para moderar opiniones.
        """
        self.grupos = grupos
        self.R_max = R_max
        self.num_grupos = num_grupos

    def calcular_conflicto_interno(self):
        """
        Calcula el conflicto interno de la red social usando la fórmula:
        CI = (∑ [n_i * (op1_i - op2_i)^2]) / (∑ [n_i])
        """
        suma_conflicto = sum(g.conflicto_contribucion() for g in self.grupos)
        # suma_agentes = sum(g.n for g in self.grupos)
        return suma_conflicto / self.num_grupos if self.num_grupos != 0 else 0

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
        return RedSocial(nuevos_grupos, self.R_max, self.num_grupos)

    def calcular_esfuerzo_total(self, estrategia):
        """
        Calcula el esfuerzo total de una estrategia.
        Suma el esfuerzo de cada grupo usando su método calcular_esfuerzo.
        """
        return sum(grupo.calcular_esfuerzo(e) for grupo, e in zip(self.grupos, estrategia))

    def modciFB(self, stop_event=None):
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
            # Verificar si se debe cancelar
            if stop_event and stop_event.is_set():
                raise Exception("Cancelado por el usuario")
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

    def modciV(self, stop_event=None):
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
                # Verificar si se debe cancelar
                if stop_event and stop_event.is_set():
                    raise Exception("Cancelado por el usuario")
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

        valor_conflicto = conflicto_total / self.num_grupos if self.num_grupos > 0 else 0

        return estrategia, costo_total, valor_conflicto

    def modciDP(self, stop_event=None):
        """
        Resuelve el problema mediante Programación Dinámica.

        Se define un DP con dimensión [i][c], donde i es el índice del grupo
        y c es el costo acumulado hasta ese posición. Cada estado DP[i][c] almacena
        una tupla (num, decisiones), donde:
        - num: suma acumulada de (n_i - e_i) * (|op1_i - op2_i|)^2
        - decisiones: lista de decisiones (e_i) para los grupos 0 a i-1.

        Se retorna la estrategia (lista de e_i), el costo total y el conflicto obtenido,
        siendo conflicto = num / num_grupos, donde num_grupos es un atributo de la red.
        """

        N = len(self.grupos)
        costo_max = self.R_max

        # DP[i] será un diccionario que mapea costo acumulado -> (num, decisiones)
        DP = [dict() for _ in range(N + 1)]
        # Estado inicial: ningún grupo procesado, costo 0, num = 0, sin decisiones.
        DP[0][0] = (0, [])

        for i in range(N):
            grupo = self.grupos[i]
            diferencia = abs(grupo.op1 - grupo.op2)  # diferencia absoluta
            for costo_acumulado, (num_acumulado, decisiones_acumuladas) in DP[i].items():
                # Verificar si se debe cancelar
                if stop_event and stop_event.is_set():
                    raise Exception("Cancelado por el usuario")
                # Para cada opción de moderar e agentes en el grupo i
                for e in range(grupo.n + 1):
                    costo_i = math.ceil(diferencia * grupo.rig * e)
                    nuevo_costo = costo_acumulado + costo_i
                    if nuevo_costo > costo_max:
                        continue  # No se puede usar si excede el presupuesto
                    nuevo_num = num_acumulado + (grupo.n - e) * (diferencia ** 2)
                    nuevas_decisiones = decisiones_acumuladas + [e]
                    # Calculamos el conflicto para este estado: nuevo_num / self.num_grupos
                    nuevo_conflicto = nuevo_num / self.num_grupos

                    # Actualizamos DP[i+1] para el nuevo costo.
                    if nuevo_costo not in DP[i + 1]:
                        DP[i + 1][nuevo_costo] = (nuevo_num, nuevas_decisiones)
                    else:
                        num_existente, _ = DP[i + 1][nuevo_costo]
                        conflicto_existente = num_existente / self.num_grupos
                        if nuevo_conflicto < conflicto_existente:
                            DP[i + 1][nuevo_costo] = (nuevo_num, nuevas_decisiones)

        # Después de procesar todos los grupos, buscamos el estado con costo <= R_max que minimice el conflicto.
        mejor_conflicto = float('inf')
        mejor_estado = None
        mejor_costo = None
        for costo, (num, decisiones) in DP[N].items():
            valor_conflicto = num / self.num_grupos
            if valor_conflicto < mejor_conflicto:
                mejor_conflicto = valor_conflicto
                mejor_estado = decisiones
                mejor_costo = costo

        return mejor_estado, mejor_costo, mejor_conflicto
