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
            resultados = {}

            # Para cada algoritmo seleccionado se obtiene su resultado
            if "FB" in seleccionados:
                estrategia, esfuerzo, conflicto = red_social.modciFB()
                resultados["Fuerza Bruta"] = (estrategia, esfuerzo, conflicto)
            if "V" in seleccionados:
                estrategia, esfuerzo, conflicto = red_social.modciV()
                resultados["Algoritmo Voraz"] = (estrategia, esfuerzo, conflicto)
            if "DP" in seleccionados:
                estrategia, esfuerzo, conflicto = red_social.modciDP()
                resultados["Programación Dinámica"] = (estrategia, esfuerzo, conflicto)

            if not resultados:
                flash("Debe seleccionar al menos una estrategia.")
                return redirect(request.url)

            return render_template("resultado.html",
                                   entrada=contenido,
                                   resultados=resultados)
        except Exception as e:
            flash(f"Error al procesar el archivo: {e}")
            return redirect(request.url)
    return render_template("index.html")
