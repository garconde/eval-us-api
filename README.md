# 🧪 Evaluador de Usabilidad

## 📌 Descripción

**Evaluador de Usabilidad** es una API desarrollada en Python que permite gestionar evaluaciones de usabilidad de softwares. A través de una interfaz web sencilla, puedes registrar aplicaciones, realizar evaluaciones y obtener métricas clave como **eficacia**, **eficiencia** y **satisfacción**. Además, incluye análisis de sentimientos y traducción automática para enriquecer los resultados.

Este proyecto fue desarrollado por **David Garcés Conde [(@garconde)](https://github.com/garconde)**.

🔗 Repositorio: [https://github.com/garconde/eval-us-api/](https://github.com/garconde/eval-us-api/)

📄 Documentación del proyecto y anexos (manual de usuario, documento de investigación, etc.):  
[https://github.com/garconde/trabajo-grado-2025](https://github.com/garconde/trabajo-grado-2025)

---

## 🚀 Características

- Desarrollo web con **Flask**.
- Soporte para CORS usando **Flask-CORS**.
- Base de datos ligera con **TinyDB**.
- Análisis de sentimientos de respuestas con **VADER Sentiment**.
- Traducción automática de textos con **Argos Translate**.
- Cálculo automatizado de métricas de usabilidad: eficacia, eficiencia y satisfacción.

---

## 📂 Estructura del Proyecto

### `main.py`

Archivo principal de la aplicación. Contiene:

- Rutas para crear, listar y gestionar softwares y evaluaciones.
- Lógica para calcular métricas de usabilidad.
- Manejo de la base de datos con TinyDB.
- Integración con VADER para análisis de sentimientos.
- Traducción automática con Argos Translate.

📅 Fecha de creación: *15 de junio de 2023*  
👤 Autor: *David Garcés Conde [(@garconde)](https://github.com/garconde)*

📌 **Recomendación:** revisa la documentación interna del código para entender la lógica y parámetros de cada método.

---

## ⚙️ Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/garconde/eval-us-api.git
   cd eval-us-api

2. (Opcional) Crea un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa: venv\Scripts\activate

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt

4. Ejecuta la aplicación:

   ```bash
   python main.py

Esto iniciará el servidor local en `http://localhost:5000` (por defecto).

---

## 🧪 Uso

Una vez ejecutado `main.py`, la API estará disponible en `http://localhost:5000`.

### Cliente Recomendado: `eval-us-app`

Se recomienda utilizar el cliente **`eval-us-app`** para interactuar con esta API de manera más sencilla. Este cliente proporciona una interfaz gráfica para facilitar la creación y gestión de registros, evaluaciones y resultados.

Puedes encontrar el repositorio de `eval-us-app` aquí:  
[https://github.com/garconde/eval-us-app/](https://github.com/garconde/eval-us-app/)

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la **Licencia MIT**. 

Puedes consultar el texto completo de la licencia en [este enlace](https://opensource.org/licenses/MIT).

---

MIT License

Copyright (c) 2023 David Garcés Conde