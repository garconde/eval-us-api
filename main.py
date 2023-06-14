from datetime import datetime
from flask import Flask, request, render_template
from tinydb import TinyDB, Query
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer




# inicializar base de datos
base_de_datos = TinyDB("base_de_datos.json")

# crear tablas
softwares = base_de_datos.table("softwares")
evaluaciones = base_de_datos.table("evaluaciones")
resultados = base_de_datos.table("resultados")

# constante para indicar que no hay valor
SIN_VALOR = -1






app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)






@app.route('/')
def index():
    return render_template('index.html')







@app.route('/nuevo_soft', methods=['POST'])
def nuevo_software():
    """
    {
      "nombre": "soft1",
      "version": "2.0.2"
    }
    """
    soft = request.json

    software = {
        "id": SIN_VALOR,
        "nombre": soft["nombre"],
        "version": soft["version"],
        "analizado": False,
        "fecha": datetime.now().timestamp(),
        "eficacia": SIN_VALOR,
        "eficiencia": SIN_VALOR,
        "satisfaccion_pun": SIN_VALOR,
        "satisfaccion_com": SIN_VALOR,
        "satisfaccion": SIN_VALOR,
        "usabilidad": SIN_VALOR,
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
        "tareas": [],
        "tiempos": [],
        "puntajes": [],
        "comentarios": []
    }

    resultados.insert(resultado)

    return "Software creado exitosamente" # separar por funciones

@app.route('/listar')
def listar():
    return softwares.all()

@app.route('/eliminar_soft', methods=['POST'])
def eliminar_soft():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 1
    }
    """

    r = request.json

    softwares.remove(Query().id == r["id_soft"])
    evaluaciones.remove(Query().id_soft == r["id_soft"])
    resultados.remove(Query().id_soft == r["id_soft"])

    return "Borrado exitosamente"  # añadir condición de si fue eliminado...







@app.route('/guardar_tareas', methods=['POST'])
def guardar_tareas(): #validar valores
    # Listo: recibir este json y actualizar
    """
    {
		"id_soft": 1,

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

@app.route('/guardar_tiempos', methods=['POST'])
def guardar_tiempos():
    # Listo: recibir este json y actualizar
    """
    {
        "id_soft": 1,

        "tiempos":[
			[7, 9, 5],
			[4, 8, 4],
			[4, 10, 5],
			[8, 4, 7],
			[10, 12, 4],
			[7, 5, 2]
		]
    }
    """



    print(r["tiempos"])

    # evaluaciones.update({"tiempos": r["tiempos"]}, Query().id_soft == r["id_soft"])

    print(r["tiempos"])
    # calcular_eficiencia(r)
    print("eficiencia calculada")

    return "Tiempos asignados exitosamente"

@app.route('/guardar_puntajes', methods=["POST"])
def guardar_puntajes():
    # Listo: recibir este json y actualizar
    """
    {
        "id_soft": 1,

        "puntajes":[
			[20, 30, 10, 25, 15],
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

    calcular_sat_puntajes(r)

    return "Puntajes asignados exitosamente"

@app.route('/guardar_comentarios', methods=["POST"])
def guardar_comentarios():
    # Listo: recibir este json y actualizar
    """
    {
        "id_soft": 1,

        "comentarios":[
			[45, 55]
			["comentario 1", "comentario 2"],
			["comentario 1", "comentario 2"]
		]
    }
    """

    r = request.json

    evaluaciones.update({"comentarios": r["comentarios"]}, Query().id_soft == r["id_soft"])

    calcular_sat_comentarios(r)

    return "Comentarios asignados exitosamente"








def calcular_eficacia(r): # Hacer validaciones

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

    eficacia_porcentaje = round(sum(eficacia_usuarios)/len(eficacia_usuarios))

    resultados.update({"tareas": eficacia_usuarios}, Query().id_soft == r["id_soft"])
    softwares.update({"eficacia": eficacia_porcentaje}, Query().id == r["id_soft"])

    es_analizado(r["id_soft"])

def calcular_eficiencia(r):  # Hacer validaciones

    print("r: ", r)

    eficiencia_usuarios = []
    referencias = r["tiempos"][0]

    for tiempo in r["tiempos"][1:]:

        cont = 0
        valores = []

        for e in tiempo:
            operacion = referencias[cont] / e
            valores.append(operacion)
            cont = cont + 1

            #print("valores: ", valores)

        prom_usuario = (sum(valores) / len(valores))
        porcentaje_usuario = round(prom_usuario * 100)
        eficiencia_usuarios.append(porcentaje_usuario)

    eficiencia_porcentaje = round(sum(eficiencia_usuarios) / len(eficiencia_usuarios))

    resultados.update({"tiempos": eficiencia_usuarios}, Query().id_soft == r["id_soft"])
    softwares.update({"eficiencia": eficiencia_porcentaje}, Query().id == r["id_soft"])

    es_analizado(r["id_soft"])

def calcular_sat_puntajes(r): #Hacer validaciones
    puntajes_usuarios = []
    pesos = r["puntajes"][0]

    for puntaje in r["puntajes"][1:]:

            cont = 0
            valores = []

            for e in puntaje:
                operacion = e * pesos[cont]
                valores.append(operacion)
                cont = cont + 1
                
            porcentaje_usuario = round(sum(valores) / sum(pesos))
            puntajes_usuarios.append(porcentaje_usuario)

    puntajes_porcentaje = round(sum(puntajes_usuarios)/len(puntajes_usuarios))

    resultados.update({"puntajes": puntajes_usuarios}, Query().id_soft == r["id_soft"])

    softwares.update({"satisfaccion_pun": puntajes_porcentaje}, Query().id == r["id_soft"])

    calcular_satisfaccion(r["id_soft"])

def calcular_sat_comentarios(r):
    #Seguir con esto guiandose de la diapositiva y el colab. -------------------------------------------------------------

    comentario_usuarios = []
    pesos = r["comentarios"][0]

    analizador = SentimentIntensityAnalyzer()

    for comentario in r["comentarios"][1:]:
        cont = 0
        valores = []

        for e in comentario:

            puntaje = analizador.polarity_scores(e)
            valor_compuesto = puntaje['compound']

            # Convertir el valor compuesto a un porcentaje de satisfacción
            porcentaje = round(((valor_compuesto + 1) / 2) * 100)
            valores.append(round((porcentaje * pesos[cont])))
            cont = cont + 1

        porcentaje_usuario = round((sum(valores) / sum(pesos)))
        comentario_usuarios.append(porcentaje_usuario)

def calcular_satisfaccion(id_soft):
    sat_pun = softwares.get(Query().id == id_soft)["satisfaccion_pun"]
    sat_com = softwares.get(Query().id == id_soft)["satisfaccion_com"]

    if sat_pun == SIN_VALOR or sat_com == SIN_VALOR:
        softwares.update({"satisfaccion": SIN_VALOR}, Query().id == id_soft)
    else:
        softwares.update({"satisfaccion": round((sat_pun + sat_com) / 2)}, Query().id == id_soft)

    es_analizado(id_soft)

def es_analizado(id_soft):
    eficacia = softwares.get(Query().id == id_soft)["eficacia"]
    eficiencia = softwares.get(Query().id == id_soft)["eficiencia"]
    satisfaccion = softwares.get(Query().id == id_soft)["satisfaccion"]

    if eficacia > SIN_VALOR and eficiencia > SIN_VALOR and satisfaccion > SIN_VALOR:
        softwares.update({"analizado": True}, Query().id == i)







@app.route('/obtener_tareas', methods=['POST'])
def obtener_tareas():
    # Listo: recibir este json y devolver lo solicitado
    """
    {
        "id_soft": 1
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
        "id_soft": 1
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
        "id_soft": 1
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
        "id_soft": 1
    }
    """

    r = request.json

    comentarios = evaluaciones.get(Query().id_soft == r["id_soft"])

    return comentarios["comentarios"] #añadir condición de si no está...





'''

################################################## Hacer toda la documentación usando docstrings ##################################################
################################################## Definir si usar swagger y/o MkDoc ##################################################


Este método recibe un json con los tiempos de cada usuario y los guarda en la base de datos.
Luego, calcula la eficiencia de cada usuario y la guarda en una lista.
Finalmente, calcula la eficiencia promedio de todos los usuarios y la guarda en la base de datos.
'''