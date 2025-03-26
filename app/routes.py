import os
import time
import threading
import itertools
from flask import render_template, request, redirect, flash, jsonify
from app import app
from app.logic.utils import parsear_entrada, formatear_salida
from app.logic.models import RedSocial

# Variable global para almacenar resultados parciales de cada algoritmo.
processing_results = {}

def run_modci(alg_key, red_social, funcion, nombre_base):
    """
    Ejecuta la función correspondiente (modciFB, modciV o modciDP),
    guarda el resultado y escribe el archivo de salida.
    """
    start_time = time.time()
    if funcion == "modciFB":
        estrategia, esfuerzo, conflicto = red_social.modciFB()
    elif funcion == "modciV":
        estrategia, esfuerzo, conflicto = red_social.modciV()
    elif funcion == "modciDP":
        estrategia, esfuerzo, conflicto = red_social.modciDP()
    else:
        return
    end_time = time.time()
    tiempo_ejecucion = end_time - start_time

    # Formateamos la salida usando la función unificada.
    salida_texto = formatear_salida(red_social, estrategia, esfuerzo, conflicto)
    # Crear carpeta outputs si no existe.
    outputs_dir = os.path.join(os.getcwd(), "outputs")
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    # Nombre del archivo: output_{nombre_base}_{funcion}.txt
    nombre_archivo = f"output_{nombre_base}_{funcion}.txt"
    ruta_salida = os.path.join(outputs_dir, nombre_archivo)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(salida_texto)

    # Almacenar el resultado junto con el nombre del archivo generado.
    processing_results[alg_key] = {
        "result": (estrategia, esfuerzo, conflicto),
        "time": tiempo_ejecucion,
        "status": "completed",
        "archivo": nombre_archivo
    }

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
            # Parsear la entrada para obtener la RedSocial.
            red_social = parsear_entrada(contenido)
            # Obtener la lista de estrategias seleccionadas.
            seleccionados = request.form.getlist("strategies")
            if not seleccionados:
                flash("Debe seleccionar al menos una estrategia.")
                return redirect(request.url)

            # Diccionario para mapear el valor del checkbox con (nombre a mostrar, nombre de la función).
            mapping_algoritmos = {
                "FB": ("Fuerza Bruta", "modciFB"),
                "V": ("Algoritmo Voraz", "modciV"),
                "DP": ("Programación Dinámica", "modciDP")
            }

            # Reiniciar los resultados de procesamiento.
            global processing_results
            processing_results = {}

            # Crear carpeta outputs si no existe.
            outputs_dir = os.path.join(os.getcwd(), "outputs")
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
            # Nombre base del archivo subido (sin extensión).
            nombre_base = os.path.splitext(archivo.filename)[0]

            # Iniciar hilos para cada algoritmo seleccionado.
            for key in seleccionados:
                _, funcion = mapping_algoritmos[key]
                t = threading.Thread(target=run_modci, args=(key, red_social, funcion, nombre_base))
                t.start()

            # Guardar también el nombre base para generar el nombre del archivo de salida.
            processing_results["nombre_base"] = nombre_base

            # Se pasa mapping_algoritmos a la plantilla para que el JS lo use.
            return render_template("lazy_results.html", entrada=contenido, mapping_algoritmos=mapping_algoritmos)
        except Exception as e:
            flash(f"Error al procesar el archivo: {e}")
            return redirect(request.url)
    return render_template("index.html")

@app.route("/status", methods=["GET"])
def status():
    """
    Devuelve en formato JSON el estado actual del procesamiento.
    """
    return jsonify(processing_results)
