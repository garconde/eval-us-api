from datetime import datetime

import tinydb
from flask import Flask, request, render_template
from textblob import TextBlob
from tinydb import TinyDB, Query, where

app = Flask(__name__)

base_de_datos = TinyDB("base_de_datos.json")
softwares = base_de_datos.table("softwares")
evaluaciones = base_de_datos.table("evaluaciones")
resultados = base_de_datos.table("resultados")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/listar')
def listar():
    return softwares.all()


@app.route('/nuevo_soft', methods=['POST'])
def nuevo_software():
    """
    {
      "nombre": "soft5",
      "version": "2.0.2"
    }
    """
    soft = request.json

    software = {
        "id": 0,
        "nombre": soft["nombre"],
        "version": soft["version"],
        "analizado": False,
        "fecha_evaluacion": datetime.now().timestamp(),
        "eficacia_porcentaje": 0,
        "eficiencia_porcentaje": 0,
        "satisfaccion_porcentaje": 0,
        "usabilidad_porcentaje": 0,
    }

    id_gen = softwares.insert(software)

    softwares.update({"id": id_gen}, doc_ids={id_gen})

    evaluacion = {
        "id_soft": id_gen,
        "tareas": [],
        "tiempos": [],
        "puntajes": [],
        "comentarios": []
    }

    evaluaciones.insert(evaluacion)

    resultado = {
        "id_soft": id_gen,
        "eficacia": [],
        "eficiencia": [],
        "satifaccion_puntajes": [],
        "satisfaccion_comentarios": []
    }

    resultados.insert(resultado)

    return "Software creado exitosamente" #separar por funciones

    # Listo: crear una evaluación vacia asociada al soft creado

@app.route('/guardar_tareas', methods=['POST'])
def guardar_tareas(): #validar valores
    # Listo: recibir este json y actualizar
    """
    {
		"id_soft": 24,

		"tareas":[
			[5, 4, 3],
			[5, 3, 4],
			[2, 4, 3],
			[2, 1, 3],
			[3, 2, 3],
			[4, 4, 2]
		]
    }
    """

    r = request.json

    evaluaciones.update({"tareas": r["tareas"]}, Query().id_soft == r["id_soft"])
    #validar valores antes de calcular

    calcular_eficacia(r)

    return "Tareas asignadas exitosamente"

def calcular_eficacia(r): #Hacer validaciones

    eficacia_usuarios = []
    referencias = r["tareas"][0]

    for tarea in r["tareas"][1:]:

        cont = 0
        valores = []

        for e in tarea:
            operacion = e / referencias[cont]
            valores.append(operacion)
            cont = cont + 1
        prom_usuario = (sum(valores) / len(valores))
        porcentaje_usuario = round(prom_usuario * 100)
        eficacia_usuarios.append(porcentaje_usuario)

    eficacia = (sum(eficacia_usuarios)/len(eficacia_usuarios))
    eficacia_porcentaje = round(eficacia)

    resultados.update({"eficacia": eficacia_usuarios}, Query().id_soft == r["id_soft"])
    softwares.update({"eficacia_porcentaje": eficacia_porcentaje}, Query().id == r["id_soft"])


@app.route('/guardar_tiempos', methods=["POST"])
def guardar_tiempos():
    # Listo: recibir este json y actualizar
    """
    {
        "id_soft": 24,

        "tiempos":[
			[7, 9, 5]
			[4, 8, 4],
			[4, 10, 5],
			[8, 4, 7],
			[10, 12, 4],
			[7, 5, 2]
		]
    }
    """

    r = request.json

    evaluaciones.update({"tiempos": r["tiempos"]}, Query().id_soft == r["id_soft"])

    calcular_eficiencia(r)

    return "Tiempos asignados exitosamente"

def calcular_eficiencia(r):


@app.route('/guardar_puntajes', methods=["POST"])
def guardar_puntajes():
    # Listo: recibir este json y actualizar
    """
    {
        "id_soft": 24,

        "puntajes":[
			[20, 30, 10, 20, 10]
			[4, 5, 4, 4, 3],
			[4, 5, 5, 3, 2],
			[3, 4, 4, 3, 2],
			[5, 4, 2, 4, 3],
			[3, 4, 3, 3, 5]
		]
    }
    """

    r = request.json

    evaluaciones.update({"puntajes": r["puntajes"]}, Query().id_soft == r["id_soft"])

    return "Puntajes asignados exitosamente"

@app.route('/guardar_comentarios', methods=["POST"])
def guardar_comentarios():
    # Listo: recibir este json y actualizar
    """
    {
        "id_soft": 24,

        "comentarios":[
			[45, 55]
			["comentario 1", "comentario 2"],
			["comentario 1", "comentario 2"]
		]
    }
    """

    r = request.json

    evaluaciones.update({"comentarios": r["comentarios"]}, Query().id_soft == r["id_soft"])

    return "Comentarios asignados exitosamente"



@app.route('/obtener_tareas', methods=['POST'])
def obtener_tareas():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 24
    }
    """

    r = request.json

    tareas = evaluaciones.get(Query().id_soft == r["id_soft"])

    return tareas["tareas"] #añadir condición de si no está...

@app.route('/obtener_tiempos', methods=['POST'])
def obtener_tiempos():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 24
    }
    """

    r = request.json

    tiempos = evaluaciones.get(Query().id_soft == r["id_soft"])

    return tiempos["tiempos"] #añadir condición de si no está...

@app.route('/obtener_puntajes', methods=['POST'])
def obtener_puntajes():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 24
    }
    """

    r = request.json

    puntajes = evaluaciones.get(Query().id_soft == r["id_soft"])

    return puntajes["puntajes"] #añadir condición de si no está...

@app.route('/obtener_comentarios', methods=['POST'])
def obtener_comentarios():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 24
    }
    """

    r = request.json

    comentarios = evaluaciones.get(Query().id_soft == r["id_soft"])

    return comentarios["comentarios"] #añadir condición de si no está...






@app.route('/analizar_comentarios', methods=['POST'])
def analizar_comentarios():
    comentarios = request.json['comentarios']  # Obtener la lista de comentarios del cuerpo de la solicitud

    print("algo: ", request.json['comentarios'])

    resultados = []
    for comentario in comentarios:
        # Crear un objeto TextBlob para el comentario
        blob = TextBlob(comentario)

        # Calcular la polaridad del comentario (-1 a 1)
        polaridad = blob.sentiment.polarity

        # Determinar el nivel de satisfacción del comentario
        if polaridad > 0:
            satisfaccion = 'Positivo'
        elif polaridad < 0:
            satisfaccion = 'Negativo'
        else:
            satisfaccion = 'Neutro'

        # Agregar el resultado a la lista de resultados
        resultados.append({'comentario': comentario, 'polaridad': polaridad, 'satisfaccion': satisfaccion})

    return {'resultados': resultados}


@app.route('/eliminar_soft', methods=['POST'])
def eliminar_soft():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 24
    }
    """

    r = request.json

    softwares.remove(Query().id == r["id_soft"])
    evaluaciones.remove(Query().id_soft == r["id_soft"])

    return "Borrado exitosamente"  # añadir condición de si fue eliminado...


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
