import os
import time
import threading
from flask import render_template, request, redirect, flash, jsonify, send_from_directory
from app import app
from app.logic.utils import parsear_entrada, formatear_salida

# Variable global para almacenar resultados parciales de cada algoritmo.
processing_results = {}
# Almacena hilos activos y sus banderas de cancelación
active_threads = {}

def run_modci(alg_key, red_social, funcion, nombre_base, stop_event):
    """
    Ejecuta la función correspondiente (modciFB, modciV o modciDP),
    guarda el resultado y escribe el archivo de salida.
    """
    try:
        start_time = time.time()
        if funcion == "modciFB":
            estrategia, esfuerzo, conflicto = red_social.modciFB(stop_event)
        elif funcion == "modciV":
            estrategia, esfuerzo, conflicto = red_social.modciV(stop_event)
        elif funcion == "modciDP":
            estrategia, esfuerzo, conflicto = red_social.modciDP(stop_event)
        else:
            return
    except Exception as e:
        processing_results[alg_key] = {
            "status": "canceled",
            "error": str(e)
        }
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
                stop_event = threading.Event()
                t = threading.Thread(
                    target=run_modci,
                    args=(key, red_social, funcion, nombre_base, stop_event)
                )
                active_threads[key] = {
                    "thread": t,
                    "stop_event": stop_event
                }
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


@app.route("/cancel", methods=["POST"])
def cancel():
    global active_threads, processing_results
    data = request.get_json()
    algorithms_to_cancel = data.get("algorithms", [])

    for alg_key in algorithms_to_cancel:
        if alg_key in active_threads:
            active_threads[alg_key]["stop_event"].set()
            processing_results[alg_key] = {"status": "canceled"}

    return jsonify({"status": "cancellation requested"})


@app.route('/outputs/<path:filename>')
def download_file(filename):
    """
    Sirve los archivos generados en la carpeta outputs.
    """
    outputs_dir = os.path.join(os.getcwd(), "outputs")
    return send_from_directory(outputs_dir, filename)