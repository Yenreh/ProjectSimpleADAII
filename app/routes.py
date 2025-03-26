import os
import time
from flask import render_template, request, redirect, flash
from app import app
from app.logic.utils import parsear_entrada, formatear_salida
from app.logic.models import RedSocial

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "archivo" not in request.files:
            flash("No se encontró ningún archivo.")
            return redirect(request.url)
        archivo = request.files["archivo"]
        if archivo.filename == "":
            flash("No se seleccionó ningún archivo.")
            return redirect(request.url)
        try:
            contenido = archivo.read().decode("utf-8")
            # Parseamos la entrada para obtener la RedSocial
            red_social = parsear_entrada(contenido)
            # Obtenemos la lista de estrategias seleccionadas
            seleccionados = request.form.getlist("strategies")
            if not seleccionados:
                flash("Debe seleccionar al menos una estrategia.")
                return redirect(request.url)

            # Diccionario para mapear el valor del checkbox con (nombre a mostrar, nombre de la función)
            mapping_algoritmos = {
                "FB": ("Fuerza Bruta", "modciFB"),
                "V": ("Algoritmo Voraz", "modciV"),
                "DP": ("Programación Dinámica", "modciDP")
            }

            resultados = {}  # key: "FB", "V", "DP"; value: (estrategia, esfuerzo, conflicto, archivo_salida, tiempo_ejecucion)

            # Crear carpeta outputs si no existe
            outputs_dir = os.path.join(os.getcwd(), "outputs")
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
            # Nombre base del archivo subido (sin extensión)
            nombre_base = os.path.splitext(archivo.filename)[0]

            # Procesar cada algoritmo seleccionado y generar su archivo de salida
            for key in seleccionados:
                nombre_alg, funcion = mapping_algoritmos[key]
                start_time = time.time()
                if funcion == "modciFB":
                    estrategia, esfuerzo, conflicto = red_social.modciFB()
                    # print("Procesando Fuerza Bruta")
                    # print(estrategia, esfuerzo, conflicto)
                elif funcion == "modciV":
                    estrategia, esfuerzo, conflicto = red_social.modciV()
                    # print("Procesando Voraz")
                    # print(estrategia, esfuerzo, conflicto)
                elif funcion == "modciDP":
                    estrategia, esfuerzo, conflicto = red_social.modciDP()
                    # print("Procesando DP")
                    # print(estrategia, esfuerzo, conflicto)
                else:
                    continue
                end_time = time.time()
                tiempo_ejecucion = end_time - start_time

                # Formateamos la salida (sin encabezados con el nombre del algoritmo)
                salida_texto = formatear_salida(red_social, estrategia, esfuerzo, conflicto)
                # Nombre del archivo: output_{nombre_base}_{nombre_algoritmo}.txt
                nombre_archivo_salida = f"output_{nombre_base}_{funcion}.txt"
                ruta_salida = os.path.join(outputs_dir, nombre_archivo_salida)
                with open(ruta_salida, "w", encoding="utf-8") as f:
                    f.write(salida_texto)
                # Almacenar resultado junto con el nombre del archivo generado y el tiempo de ejecución
                resultados[key] = (estrategia, esfuerzo, conflicto, nombre_archivo_salida, tiempo_ejecucion)

            # Para mostrar en la plantilla se mapea el código al nombre a mostrar
            resultados_mostrar = {}
            for key, datos in resultados.items():
                nombre_alg, _ = mapping_algoritmos[key]
                resultados_mostrar[nombre_alg] = datos

            return render_template("resultado.html",
                                   entrada=contenido,
                                   resultados=resultados_mostrar)
        except Exception as e:
            flash(f"Error al procesar el archivo: {e}")
            return redirect(request.url)
    return render_template("index.html")