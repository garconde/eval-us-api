"""
main.py

Descripción: Este archivo contiene la implementación de un sistema de gestión de evaluaciones de usabilidad de
softwares, que incluye rutas para gestionar los softwares, obtener datos de la base de datos, y métodos para calcular
la eficacia, eficiencia y satisfacción. También se encarga de la creación de nuevos softwares, evaluaciones y
resultados.

Fecha: 15 de junio de 2023
Autor: David Garcés Conde (@garconde)

Detalles:
- Importa bibliotecas como VADER, Flask, datetime, TinyDB, entre otras.
- Se recomienda leer la documentación interna de cada método para entender su funcionalidad y parámetros.


TODO:
* Separar por funciones usando BluePrint
* Gestionar las demás vistas
* Reestructurar el proyecto en carpetas
"""


from datetime import datetime
from flask import Flask, request, render_template, jsonify
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






# Crea una instancia de la aplicación Flask
app = Flask(__name__) #





# Rutas de la API para la gestión de las plantillas para las vistas del aplicativo
@app.route('/')
def index():
    """
    Renderiza la página de inicio.

    Valor de retorno:
    Una respuesta que renderiza la plantilla "index.html".

    Notas:
    - Se asume que se tiene un template llamado "index.html" disponible.
    """

    return render_template('index.html')







# Rutas de la API para la gestion, listado y eliminación de softwares en la base de datos
@app.route('/nuevo_soft', methods=['POST'])
def nuevo_software():
    """
    Crea un nuevo software.

    Entrada (request JSON):
    {
        "nombre": "soft1",
        "version": "2.0.2"
    }

    Valor de retorno:
    Una respuesta en formato JSON que indica si el software fue creado exitosamente o no.

    Notas:
    - La constante SIN_VALOR está definida con su respectivo valor.
    """

    # Verificar si el campo "nombre" y "version" están presentes en la solicitud JSON
    if "nombre" not in request.json or "version" not in request.json:
        response = {"error": "Campos 'nombre' y 'version' faltantes en la solicitud"}
        return jsonify(response), 400

    soft = request.json

    # Crear el documento de software
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

    # Insertar el documento de software en la colección "softwares"
    id_gen = softwares.insert(software)

    # Actualizar el campo "id" con el ID generado
    softwares.update({"id": id_gen}, doc_ids=[id_gen])

    # Crear el documento de evaluación asociado al software
    evaluacion = {
        "id_soft": id_gen,
        "tareas": [],
        "tiempos": [],
        "puntajes": [],
        "comentarios": []
    }

    # Insertar el documento de evaluación en la colección "evaluaciones"
    evaluaciones.insert(evaluacion)

    # Crear el documento de resultado asociado al software
    resultado = {
        "id_soft": id_gen,
        "tareas": [],
        "tiempos": [],
        "puntajes": [],
        "comentarios": []
    }

    # Insertar el documento de resultado en la colección "resultados"
    resultados.insert(resultado)

    response = {"message": "Software creado exitosamente"}
    return jsonify(response)

@app.route('/listar')
def listar():
    """
    Lista todos los software disponibles.

    Valor de retorno:
    Una respuesta en formato JSON que contiene la lista de todos los software disponibles.

    Notas:
    - Se asume que la variable "softwares" contiene la colección de datos de software.
    """

    # Obtener la lista de todos los software
    lista_softwares = softwares.all()

    # Verificar si no se encontraron software
    if not lista_softwares:
        response = {"message": "No se encontraron software"}
        return jsonify(response), 404

    return jsonify(lista_softwares)

@app.route('/eliminar_soft', methods=['DELETE'])
def eliminar_soft():
    """
    Elimina un software y sus datos asociados.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una respuesta en formato JSON que indica si el borrado fue exitoso o no.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    - Las tablas "softwares", "evaluaciones" y "resultados" contienen las colecciones de datos correspondientes.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Eliminar el software y sus datos asociados
    softwares.remove(Query().id == id_soft)
    evaluaciones.remove(Query().id_soft == id_soft)
    resultados.remove(Query().id_soft == id_soft)

    response = {"message": "Borrado exitosamente"}
    return jsonify(response)







# Rutas de la API para almacenar datos de evaluación en la base de datos
@app.route('/guardar_tareas', methods=["POST"])
def guardar_tareas():
    """
    Guarda en la base de datos las tareas realizadas por un usuario sobre un software específico.

    Esta función maneja una solicitud POST y espera recibir un cuerpo JSON con los siguientes campos:

        - id_soft: El ID del software.
        - tareas: Una lista de con las tareas realizadas por el usuario.
        El primer elemento de la lista contiene las referencias,
        el segundo elemento contiene la cantidad de tareas del usuario 1,
        el tercero contiene la cantidad de tareas del usuario 2 y así sucesivamente.

        Ejemplo:
        {
            "id_soft": 1,

            "tareas":[
                [5, 4, 3],
                [5, 3, 2],
                [2, 4, 3],
                [2, 1, 3],
                [3, 2, 3],
                [4, 4, 2]
            ]
        }

    Si el ID del software no existe en la base de datos, se devuelve un mensaje de error con el código de respuesta 404.

    En caso contrario, se actualiza la lista de tareas asignadas al software
    y se devuelve un mensaje de éxito con el código de respuesta 200.

    Returns:
        JSON: Un JSON con un mensaje de éxito o un mensaje de error en caso de fallo.
    """
    try:

        # Validar que se haya enviado un cuerpo JSON en la solicitud
        if not request.is_json:
            return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON"}), 400

        # Obtener los datos del JSON enviado en la solicitud
        r = request.json

        # Validar que se hayan proporcionado los campos necesarios
        if "id_soft" not in r or "tareas" not in r:
            return jsonify({"error": "Faltan campos obligatorios en el JSON"}), 400

        # Obtener el id_soft del JSON
        id_soft = r["id_soft"]

        # Verificar si el id_soft existe en la base de datos
        if not softwares.contains(doc_id=id_soft):
            return jsonify({"error": f"No se encontró el id_soft {id_soft} en la base de datos"}), 404

        # Obtener las tareas del JSON
        tareas = r["tareas"]

        # Calcular eficacia
        try:

            calcular_eficacia(id_soft, tareas)

        except ValueError as e:
            return jsonify({"error: ": str(e)}), 400
        except ZeroDivisionError as e:
            return jsonify({"error de división por cero: ": str(e)}), 400
        except Exception as e:
            return jsonify({"error inesperado: ": str(e)}), 500

        # Realizar la actualización de los datos en la base de datos
        evaluaciones.update({"tareas": tareas}, Query().id_soft == id_soft)

        return jsonify({"mensaje": "Tareas asignadas exitosamente"}), 200

    except Exception as e:
        return jsonify({"error: ": str(e)}), 500

@app.route('/guardar_tiempos', methods=["POST"])
def guardar_tiempos():
    """
    Guarda en la base de datos los tiempos tomados por un usuario al hacer tareas específico.

    Esta función maneja una solicitud POST y espera recibir un cuerpo JSON con los siguientes campos:

        - id_soft: El ID del software.
        - tiempos: Una lista de con las tareas realizadas por el usuario.
        El primer elemento de la lista contiene las referencias,
        el segundo elemento contiene la cantidad de tareas del usuario 1,
        el tercero contiene la cantidad de tareas del usuario 2 y así sucesivamente.

        Ejemplo:
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

    Si el ID del software no existe en la base de datos, se devuelve un mensaje de error con el código de respuesta 404.

    En caso contrario, se actualiza la lista de tareas asignadas al software
    y se devuelve un mensaje de éxito con el código de respuesta 200.

    Returns:
        JSON: Un JSON con un mensaje de éxito o un mensaje de error en caso de fallo.
    """
    try:

        # Validar que se haya enviado un cuerpo JSON en la solicitud
        if not request.is_json:
            return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON"}), 400

        # Obtener los datos del JSON enviado en la solicitud
        r = request.json

        # Validar que se hayan proporcionado los campos necesarios
        if "id_soft" not in r or "tiempos" not in r:
            return jsonify({"error": "Faltan campos obligatorios en el JSON"}), 400

        # Obtener el id_soft del JSON
        id_soft = r["id_soft"]

        # Verificar si el id_soft existe en la base de datos
        if not softwares.contains(doc_id=id_soft):
            return jsonify({"error": f"No se encontró el id_soft {id_soft} en la base de datos"}), 404

        # Obtener los tiempos del JSON
        tiempos = r["tiempos"]

        # Calcular eficacia
        try:

            calcular_eficiencia(id_soft, tiempos)

        except ValueError as e:
            return jsonify({"error: ": str(e)}), 400
        except ZeroDivisionError as e:
            return jsonify({"error de división por cero: ": str(e)}), 400
        except Exception as e:
            return jsonify({"error inesperado: ": str(e)}), 500

        # Realizar la actualización de los datos en la base de datos
        evaluaciones.update({"tiempos": tiempos}, Query().id_soft == id_soft)

        return jsonify({"mensaje": "Tiempos asignadas exitosamente"}), 200

    except Exception as e:
        return jsonify({"error: ": str(e)}), 500

@app.route('/guardar_puntajes', methods=["POST"])
def guardar_puntajes():
    """
    Guarda en la base de datos los puntajes tomados por un usuario al responder preguntas cerradas.

    Esta función maneja una solicitud POST y espera recibir un cuerpo JSON con los siguientes campos:

        - id_soft: El ID del software.
        - puntajes: Una lista de con los puntajes como respuestas de un usuario a un cuestionario.
        El primer elemento de la lista contiene los pesos de las preguntas,
        el segundo elemento contiene los puntajes de las respuestas del usuario 1,
        el tercero contiene del usuario 2 y así sucesivamente.

        Ejemplo:
        {
            "id_soft": 1,

            "puntajes":[
                [20, 30, 10, 25, 10, 5],
                [4, 5, 4, 4, 3, 4],
                [4, 5, 5, 3, 2, 5],
                [3, 4, 4, 3, 2, 1],
                [5, 4, 2, 4, 3, 2],
                [3, 4, 3, 3, 5, 3]
            ]
        }

    Si el ID del software no existe en la base de datos, se devuelve un mensaje de error con el código de respuesta 404.

    En caso contrario, se actualiza la lista de puntajes asignada al software
    y se devuelve un mensaje de éxito con el código de respuesta 200.

    Returns:
        JSON: Un JSON con un mensaje de éxito o un mensaje de error en caso de fallo.
    """
    try:

        # Validar que se haya enviado un cuerpo JSON en la solicitud
        if not request.is_json:
            return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON"}), 400

        # Obtener los datos del JSON enviado en la solicitud
        r = request.json

        # Validar que se hayan proporcionado los campos necesarios
        if "id_soft" not in r or "puntajes" not in r:
            return jsonify({"error": "Faltan campos obligatorios en el JSON"}), 400

        # Obtener el id_soft del JSON
        id_soft = r["id_soft"]

        # Verificar si el id_soft existe en la base de datos
        if not softwares.contains(doc_id=id_soft):
            return jsonify({"error": f"No se encontró el id_soft {id_soft} en la base de datos"}), 404

        # Obtener los puntajes del JSON
        puntajes = r["puntajes"]

        # Calcular satisfaccion en preguntas cerradas
        try:

            calcular_sat_puntajes(id_soft, puntajes)

        except ValueError as e:
            return jsonify({"error: ": str(e)}), 400
        except Exception as e:
            return jsonify({"error inesperado: ": str(e)}), 500

        # Realizar la actualización de los datos en la base de datos
        evaluaciones.update({"puntajes": puntajes}, Query().id_soft == id_soft)

        return jsonify({"mensaje": "Puntajes asignados exitosamente"}), 200

    except Exception as e:
        return jsonify({"error: ": str(e)}), 500

@app.route('/guardar_comentarios', methods=["POST"])
def guardar_comentarios():
    """
    Guarda en la base de datos los comentarios tomados por un usuario al responder preguntas abiertas.

    Esta función maneja una solicitud POST y espera recibir un cuerpo JSON con los siguientes campos:

        - id_soft: El ID del software.
        - puntajes: Una lista de con los puntajes como respuestas de un usuario a un cuestionario
        El primer elemento de la lista contiene los pesos de las preguntas,
        el segundo elemento contiene los comentarios del usuario 1,
        el tercero contiene del usuario 2 y así sucesivamente.

        Ejemplo:
        {
            "id_soft": 1,
            "comentarios": [
                [30, 70],
                ["Me encanta la interfaz intuitiva y fácil de usar", "No me gusta la falta de opciones de personalización"],
                ["Las características son increíbles, cumplen con todas mis necesidades", "A veces experimento problemas de rendimiento"],
                ["El soporte al cliente es excepcional, siempre resuelven mis dudas", "La falta de actualizaciones frecuentes es decepcionante"],
                ["La integración con otras herramientas es perfecta", "A veces encuentro errores que interrumpen mi flujo de trabajo"],
                ["La velocidad y eficiencia del software son impresionantes", "Algunas funciones no son tan intuitivas como me gustaría"]
            ]
        }

    Si el ID del software no existe en la base de datos, se devuelve un mensaje de error con el código de respuesta 404.

    En caso contrario, se actualiza la lista de puntajes asignada al software
    y se devuelve un mensaje de éxito con el código de respuesta 200.

    Returns:
        JSON: Un JSON con un mensaje de éxito o un mensaje de error en caso de fallo.
    """
    try:

        # Validar que se haya enviado un cuerpo JSON en la solicitud
        if not request.is_json:
            return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON"}), 400

        # Obtener los datos del JSON enviado en la solicitud
        r = request.json

        # Validar que se hayan proporcionado los campos necesarios
        if "id_soft" not in r or "comentarios" not in r:
            return jsonify({"error": "Faltan campos obligatorios en el JSON"}), 400

        # Obtener el id_soft del JSON
        id_soft = r["id_soft"]

        # Verificar si el id_soft existe en la base de datos
        if not softwares.contains(doc_id=id_soft):
            return jsonify({"error": f"No se encontró el id_soft {id_soft} en la base de datos"}), 404

        # Obtener los comentarios del JSON
        comentarios = r["comentarios"]

        # Calcular satisfaccion en preguntas abiertas
        try:

            calcular_sat_comentarios(id_soft, comentarios)

        except ValueError as e:
            return jsonify({"error: ": str(e)}), 400
        except Exception as e:
            return jsonify({"error inesperado: ": str(e)}), 500

        # Realizar la actualización de los datos en la base de datos
        evaluaciones.update({"comentarios": comentarios}, Query().id_soft == id_soft)

        return jsonify({"mensaje": "Comentarios asignados exitosamente"}), 200

    except Exception as e:
        return jsonify({"error: ": str(e)}), 500






# Funciones auxiliares para realizar los cálculos de eficacia, efiencia y satisfacción
def calcular_eficacia(id_soft, tareas):
    """
    Calcula la eficacia de las tareas asignadas a un software y actualiza los resultados.

    Args:
        id_soft (int): El ID del software.
        tareas (list): Una lista que contiene las tareas asignadas, donde cada tarea es una lista de valores.

    Raises:
        ValueError: Si el ID del software no existe en la base de datos.
        ValueError: Si la lista de tareas está vacía o contiene elementos no válidos.
        ValueError: Si algún elemento de las tareas es mayor que la referencia correspondiente.
        ZeroDivisionError: Si algunos de los elementos de la lista de referencias es cero.

    Returns:
        None
    """

    # Validar la lista de tareas
    if not isinstance(tareas, list) or len(tareas) < 2:
        raise ValueError("La lista de tareas debe contener al menos dos elementos.")

    eficacia_usuarios = []
    referencias = tareas[0]

    # Validar que la lista de referencias contenga solamente elementos numéricos
    if not all(isinstance(e, int) for e in referencias):
        raise ValueError("Los valores de la lista de referencias deben ser numéricos.")

    # Validar si algún elemento de la lista de referencias es cero
    if any(e == 0 for e in referencias):
        raise ZeroDivisionError("No se puede dividir por cero. Algún elemento de la lista de referencias es cero.")

    # Validar si algún elemento de la lista de referencias es negativo
    if any(e < 0 for e in referencias):
        raise ValueError("No se pueden proporcionar valores negativos en la lista de referencias.")

    for tarea in tareas[1:]:

        cont = 0
        valores = []

        for e in tarea:

            # Validar si los valores son numéricos
            if not isinstance(e, int):
                raise ValueError("Los valores de las tareas deben ser numéricos.")

            # Validar si algún elemento es negativo
            if e < 0:
                raise ValueError("No se pueden proporcionar valores negativos en los valores.")

            # Validar si algún elemento es mayor que los de la lista de referencias
            if e > referencias[cont]:
                raise ValueError("Los valores de las tareas no pueden ser mayores que los de la lista de referencias.")

            # Calcular la eficacia en cada tarea
            operacion = e / referencias[cont]
            valores.append(operacion)
            cont = cont + 1

        prom_usuario = (sum(valores) / len(valores))
        porcentaje_usuario = round(prom_usuario * 100)
        eficacia_usuarios.append(porcentaje_usuario)

    # Calcular la eficacia promedio
    eficacia_porcentaje = round(sum(eficacia_usuarios) / len(eficacia_usuarios))

    # Actualizar los resultados en la base de datos
    resultados.update({"tareas": eficacia_usuarios}, Query().id_soft == id_soft)
    softwares.update({"eficacia": eficacia_porcentaje}, Query().id == id_soft)

    # Actualizar el estado del software
    es_analizado(id_soft)

def calcular_eficiencia(id_soft, tiempos):
    """
    Calcula la eficiencia en las tareas asignadas a un usuario y actualiza los resultados.

    Args:
        id_soft (int): El ID del software.
        tiempos (list): Una lista que contiene los tiempos tomados, donde cada tiempo es una lista de valores.

    Raises:
        ValueError: Si el ID del software no existe en la base de datos.
        ValueError: Si la lista de tiempos está vacía o contiene elementos no válidos.
        ZeroDivisionError: Si alguno de los elementos de la lista de referencias es cero.

    Returns:
        None
    """

    # Validar la lista de tiempos
    if not isinstance(tiempos, list) or len(tiempos) < 2:
        raise ValueError("La lista de tiempos debe contener al menos dos elementos.")

    eficacia_usuarios = []
    referencias = tiempos[0]

    # Validar que la lista de referencias contenga solamente elementos numéricos
    if not all(isinstance(e, int) for e in referencias):
        raise ValueError("Los valores de la lista de referencias deben ser numéricos.")

    # Validar si algún elemento de la lista de referencias es negativo
    if any(e < 0 for e in referencias):
        raise ValueError("No se pueden proporcionar valores negativos en la lista de referencias.")

    for tiempo in tiempos[1:]:

        cont = 0
        valores = []

        for e in tiempo:

            # Validar si los valores son numéricos
            if not isinstance(e, int):
                raise ValueError("Los valores de las tiempos deben ser numéricos.")

            # Validar si algún elemento de los valores es cero
            if e == 0:
                raise ZeroDivisionError("No se puede dividir por cero. Algún valor de la lista de tiempos es cero.")

            # Validar si algún elemento es negativo
            if e < 0:
                raise ValueError("No se pueden proporcionar valores negativos en los valores.")

            # Calcular la eficiencia en cada tarea
            operacion = referencias[cont] / e
            valores.append(operacion)
            cont = cont + 1

        prom_usuario = (sum(valores) / len(valores))
        porcentaje_usuario = round(prom_usuario * 100)
        eficacia_usuarios.append(porcentaje_usuario)

    # Calcular la eficiencia promedio
    eficacia_porcentaje = round(sum(eficacia_usuarios) / len(eficacia_usuarios))

    # Actualizar los resultados en la base de datos
    resultados.update({"tiempos": eficacia_usuarios}, Query().id_soft == id_soft)
    softwares.update({"eficacia": eficacia_porcentaje}, Query().id == id_soft)

    # Actualizar el estado del software
    es_analizado(id_soft)

def calcular_sat_puntajes(id_soft, puntajes):
    """
    Calcula la satisfacción con los puntajes de las preguntas cerradas y actualiza los resultados.

    Args:
        id_soft (int): El ID del software.
        puntajes (list): Una lista que contiene los puntajes tomados, donde cada puntaje es una lista de valores.

    Raises:
        ValueError: Si el ID del software no existe en la base de datos.
        ValueError: Si la lista de puntajes está vacía o contiene elementos no válidos.

    Returns:
        None
    """

    # Validar la lista de puntajes
    if not isinstance(puntajes, list) or len(puntajes) < 2:
        raise ValueError("La lista de puntajes debe contener al menos dos elementos.")

    puntajes_usuarios = []
    pesos = puntajes[0]

    # Validar que la lista de pesos contenga solamente elementos numéricos
    if not all(isinstance(e, int) for e in pesos):
        raise ValueError("Los valores de la lista de pesos deben ser numéricos.")

    # Validar si algún elemento de la lista de pesos es negativo
    if any(e < 0 for e in pesos):
        raise ValueError("No se pueden proporcionar valores negativos en la lista de pesos.")

    for puntaje in puntajes[1:]:

        cont = 0
        valores = []

        for e in puntaje:

            # Validar si los valores son numéricos
            if not isinstance(e, int):
                raise ValueError("Los valores de las puntajes deben ser numéricos.")

            # Validar si algún elemento de los valores es cero
            if e < 1 or e > 5:
                raise ValueError("Los valores de las puntajes deben estar entre 1 y 5.")

            # Validar si algún elemento es negativo
            if e < 0:
                raise ValueError("No se pueden proporcionar valores negativos en los valores.")

            # Calcular la satisfacción en cada pregunta
            operacion = e * pesos[cont] * 20
            valores.append(operacion)
            cont = cont + 1

        porcentaje_usuario = round(sum(valores) / sum(pesos))
        puntajes_usuarios.append(porcentaje_usuario)

    # Calcular la satisfacción promedio con los puntajes
    puntajes_porcentaje = round(sum(puntajes_usuarios) / len(puntajes_usuarios))

    # Actualizar los resultados en la base de datos
    resultados.update({"puntajes": puntajes_usuarios}, Query().id_soft == id_soft)
    softwares.update({"satisfaccion_pun": puntajes_porcentaje}, Query().id == id_soft)

    # Calcular la satisfacción general
    calcular_satisfaccion(id_soft)

def calcular_sat_comentarios(id_soft, comentarios):
    """
        Calcula la satisfacción con los puntajes de las preguntas abiertas y actualiza los resultados.

        Args:
            id_soft (int): El ID del software.
            comentarios (list): Una lista que contiene los comentarios tomados, donde cada comentario es una lista de valores.

        Raises:
            ValueError: Si el ID del software no existe en la base de datos.
            ValueError: Si la lista de comentarios está vacía o contiene elementos no válidos.

        Returns:
            None
        """

    # Validar la lista de puntajes
    if not isinstance(comentarios, list) or len(comentarios) < 2:
        raise ValueError("La lista de puntajes debe contener al menos dos elementos.")

    comentarios_usuarios = []
    pesos = comentarios[0]

    # Analizador de sentimientos de VADER (Valence Aware Dictionary and sEntiment Reasoner) para comentarios
    analizador = SentimentIntensityAnalyzer()

    for comentario in comentarios[1:]:
        cont = 0
        valores = []

        for e in comentario:

            # Validar si los valores son cadena de texto
            if not isinstance(e, str):
                raise ValueError("Los valores de las puntajes deben ser cadenas de texto.")

            # Calcular el nivel de satisfacción de cada comentario
            puntaje = analizador.polarity_scores(e)

            # Obtener el valor compuesto del comentario
            valor_compuesto = puntaje['compound']

            # Convertir el valor compuesto a un porcentaje de satisfacción
            porcentaje = round(((valor_compuesto + 1) / 2) * 100)
            valores.append(round((porcentaje * pesos[cont])))
            cont = cont + 1

        porcentaje_usuario = round((sum(valores) / sum(pesos)))
        comentarios_usuarios.append(porcentaje_usuario)

    # Calcular la satisfacción promedio con los comentarios
    comentarios_porcentaje = round(sum(comentarios_usuarios) / len(comentarios_usuarios))

    # Actualizar los resultados en la base de datos
    resultados.update({"comentarios": comentarios_usuarios}, Query().id_soft == id_soft)
    softwares.update({"satisfaccion_com": comentarios_porcentaje}, Query().id == id_soft)

    # Calcular la satisfacción general
    calcular_satisfaccion(id_soft)

def calcular_satisfaccion(id_soft):
    """
    Calcula la satisfacción de un software basado en dos valores: "satisfaccion_pun" y "satisfaccion_com".

    Parámetros:
    - id_soft: ID del software para calcular la satisfacción.

    Valor de retorno:
    No hay valor de retorno explícito.

    Notas:
    - Los valores "satisfaccion_pun" y "satisfaccion_com" deben estar en un rango específico y formato esperado.
    - El valor `SIN_VALOR` se utiliza para indicar una falta de datos en la satisfacción.
    """

    puntuacion_satisfaccion = softwares.get(Query().id == id_soft)["satisfaccion_pun"]
    comentario_satisfaccion = softwares.get(Query().id == id_soft)["satisfaccion_com"]

    # Verificar si falta algún valor de satisfacción
    if puntuacion_satisfaccion == SIN_VALOR or comentario_satisfaccion == SIN_VALOR:
        softwares.update({"satisfaccion": SIN_VALOR}, Query().id == id_soft)
    else:
        # Calcular la satisfacción promedio y redondear al entero más cercano
        satisfaccion_promedio = round((puntuacion_satisfaccion + comentario_satisfaccion) / 2)
        softwares.update({"satisfaccion": satisfaccion_promedio}, Query().id == id_soft)

    # Actualizar el estado de análisis del software
    es_analizado(id_soft)






# Función para actualizar el estado de análisis de un software en la base de datos
def es_analizado(id_soft):
    """
    Actualiza el campo 'usabilidad' de un software basado en los valores de 'eficacia', 'eficiencia' y 'satisfaccion'.

    Parámetros:
    - id_soft: ID del software a ser analizado.

    Valor de retorno:
    No hay valor de retorno explícito.

    Notas:
    - Los valores 'eficacia', 'eficiencia' y 'satisfaccion' deben estar en un rango específico y formato esperado.
    - El valor 'SIN_VALOR' se utiliza para indicar una falta de datos en las métricas.
    """

    eficacia = softwares.get(Query().id == id_soft)["eficacia"]
    eficiencia = softwares.get(Query().id == id_soft)["eficiencia"]
    satisfaccion = softwares.get(Query().id == id_soft)["satisfaccion"]

    # Verificar si todas las métricas tienen valores válidos
    if eficacia > SIN_VALOR and eficiencia > SIN_VALOR and satisfaccion > SIN_VALOR:

        # Calcular la usabilidad promedio y redondear al entero más cercano
        usabilidad = round((eficacia + eficiencia + satisfaccion) / 3)

        # Actualizar el campo 'usabilidad' del software
        softwares.update({"usabilidad": usabilidad}, Query().id == id_soft)

        # Actualizar el estado de análisis del software
        softwares.update({"analizado": True}, Query().id == id_soft)






# Rutas de la API REST para obtener datos de la base de datos a través de solicitudes HTTP

@app.route('/obtener_val_tareas', methods=['POST'])
def obtener_val_tareas():
    """
    Obtiene las tareas asociadas a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de tareas asociadas al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener la evaluación del software especificado
    evaluacion = evaluaciones.get(Query().id_soft == id_soft)

    # Verificar si se encontraron tareas para el software especificado
    if not evaluacion:
        response = {"error": "No se encontraron tareas para el software especificado"}
        return jsonify(response), 404

    return evaluacion["tareas"]

@app.route('/obtener_val_tiempos', methods=['POST'])
def obtener_val_tiempos():
    """
    Obtiene los tiempos asociados a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de tiempos asociados al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener la evaluación asociada al software especificado
    evaluacion = evaluaciones.get(Query().id_soft == id_soft)

    # Verificar si se encontraron tiempos para el software especificado
    if not evaluacion:
        response = {"error": "No se encontraron tiempos para el software especificado"}
        return jsonify(response), 404

    return evaluacion["tiempos"]

@app.route('/obtener_val_puntajes', methods=['POST'])
def obtener_val_puntajes():
    """
    Obtiene los puntajes asociados a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de puntajes asociados al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener la evaluación asociada al software especificado
    evaluacion = evaluaciones.get(Query().id_soft == id_soft)

    # Verificar si se encontraron puntajes para el software especificado
    if not evaluacion:
        response = {"error": "No se encontraron puntajes para el software especificado"}
        return jsonify(response), 404

    return evaluacion["puntajes"]

@app.route('/obtener_val_comentarios', methods=['POST'])
def obtener_val_comentarios():
    """
    Obtiene los comentarios asociados a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de comentarios asociados al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener la evaluación asociada al software especificado
    evaluacion = evaluaciones.get(Query().id_soft == id_soft)

    # Verificar si se encontraron comentarios para el software especificado
    if not evaluacion:
        response = {"error": "No se encontraron comentarios para el software especificado"}
        return jsonify(response), 404

    return evaluacion["comentarios"]

@app.route('/obtener_res_tareas', methods=['POST'])
def obtener_res_tareas():
    """
    Obtiene los resultados de las tareas asociadas a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de los cálculos hechos con las tareas asociadas al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener los resultados del software especificado
    resultado = resultados.get(Query().id_soft == id_soft)

    # Verificar si se encontraron tareas para el software especificado
    if not resultado:
        response = {"error": "No se encontraron tareas para el software especificado"}
        return jsonify(response), 404

    return resultado["tareas"]

@app.route('/obtener_res_tiempos', methods=['POST'])
def obtener_res_tiempos():
    """
    Obtiene los resultados de los tiempos asociados a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de los cálculos hechos con los tiempos asociados al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener el resultado del software especificado
    resultado = resultados.get(Query().id_soft == id_soft)

    # Verificar si se encontraron tiempos para el software especificado
    if not resultado:
        response = {"error": "No se encontraron tiempos para el software especificado"}
        return jsonify(response), 404

    return resultado["tiempos"]

@app.route('/obtener_res_puntajes', methods=['POST'])
def obtener_res_puntajes():
    """
    Obtiene los resultados de los puntajes asociados a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de los cálculos hechos con los puntajes asociados al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener el resultado del software especificado
    resultado = resultados.get(Query().id_soft == id_soft)

    # Verificar si se encontraron puntajes para el software especificado
    if not resultado:
        response = {"error": "No se encontraron puntajes para el software especificado"}
        return jsonify(response), 404

    return resultado["puntajes"]

@app.route('/obtener_res_comentarios', methods=['POST'])
def obtener_res_comentarios():
    """
    Obtiene los resultados de los comentarios asociados a un software específico.

    Entrada (request JSON):
    {
        "id_soft": 1
    }

    Valor de retorno:
    Una lista de los cálculos hechos con los comentarios asociados al software especificado.

    Notas:
    - El campo "id_soft" debe ser proporcionado en la solicitud.
    """

    # Verificar si el campo "id_soft" está presente en la solicitud JSON
    if "id_soft" not in request.json:
        response = {"error": "Campo 'id_soft' faltante en la solicitud"}
        return jsonify(response), 400

    id_soft = request.json["id_soft"]

    # Obtener el resultado del software especificado
    resultado = resultados.get(Query().id_soft == id_soft)

    # Verificar si se encontraron comentarios para el software especificado
    if not resultado:
        response = {"error": "No se encontraron comentarios para el software especificado"}
        return jsonify(response), 404

    return resultado["comentarios"]






# Fución principal para ejecutar la aplicación Flask (main) al ejecutar el archivo (python main.py)

if __name__ == '__main__':
    """
    Ejecuta la aplicación Flask.

    Notas:
    - La variable "app" contiene la instancia de la aplicación Flask.
    - La aplicación se ejecuta en el host '0.0.0.0' o localhost, en el puerto 5000.
    - El modo de depuración está comentado, pero se puede habilitar si es necesario.
    """

    # Quitar el comentario de la siguiente línea para habilitar el modo de depuración
    # app.debug = True

    app.run(host='0.0.0.0', port=5000)
