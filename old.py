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

if __name__ == "__main__":
    # Ejemplo 1:
  
# 7,33,62,0.49
# 11,-36,-1,0.364
# 12,28,27,0.326
# 2,88,36,0.153
# 6,-28,16,0.372
# 4,38,82,0.398
# 14,-54,-14,0.199
# 5,91,45,0.088
# 14,-18,13,0.316
# 12,-40,-8,0.602
# 1223
    grupos_RS1 = [
        GrupoAgentes(7, 33, 62, 0.49),
        GrupoAgentes(11, -36, -1, 0.364),
        GrupoAgentes(12, 28, 27, 0.326),
        GrupoAgentes(2, 88, 36, 0.153),
        GrupoAgentes(6, -28, 16, 0.372),
        GrupoAgentes(4, 38, 82, 0.398),
        GrupoAgentes(14, -54, -14, 0.199),
        GrupoAgentes(5, 91, 45, 0.088),
        GrupoAgentes(14, -18, 13, 0.316),
        GrupoAgentes(12, -40, -8, 0.602)
      
    ]
    R_max_RS1 = 1223
    red_social = RedSocial(grupos_RS1, R_max_RS1)

    print("Ejemplo 1:")
    estrategia, esfuerzo, conflicto = red_social.modciFB()
    print("Estrategia óptima:", estrategia)
    print("Esfuerzo total:", esfuerzo)
    print("Conflicto interno:", conflicto)