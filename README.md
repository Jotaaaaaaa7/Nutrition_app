# 🥗 Nutrición App – Plataforma de Gestión Nutricional

**Nutrición App** es una solución completa para gestionar información nutricional de alimentos, crear recetas, planificar comidas diarias y analizar nutrientes. El flujo va desde el scraping automatizado de datos nutricionales hasta una aplicación interactiva con API REST y frontend en Streamlit.

---

## 🚀 Tabla de Contenidos

- [1. Scraping de Datos](#1-scraping-de-datos)
- [2. Definición y Migración a la Base de Datos (SQLite)](#2-definición-y-migración-a-la-base-de-datos-sqlite)
- [3. API REST con FastAPI](#3-api-rest-con-fastapi)
- [4. Frontend Interactivo con Streamlit](#4-frontend-interactivo-con-streamlit)
- [5. Cómo Ejecutar el Proyecto](#5-cómo-ejecutar-el-proyecto)
- [6. Funcionalidades Clave](#6-funcionalidades-clave)


---

## 1. Scraping de Datos

El script `scrapping.py` utiliza Selenium para obtener datos de nutrientes desde la web:

- Se generan entradas de 100g por alimento.
- Los datos se almacenan en `data/alimentos.csv`.

---

## 2. Definición y Migración a la Base de Datos (SQLite)

La base de datos se define en `db_config.py` con SQLAlchemy. Utiliza SQLite para almacenamiento local.

Para resetear y poblar la base de datos:

```bash
python seeder.py
```

Esto hará:
- Inicialización de las tablas.
- Carga de alimentos desde el CSV.
- Inserción de recetas de ejemplo.
- Inserción de comidas planificadas de ejemplo.

---

## 3. API REST con FastAPI

`api.py` expone una API para operar con alimentos, recetas y comidas. Puedes lanzarla con:

```bash
uvicorn api:app --reload
```

Endpoints organizados por:

- `/foods`
- `/recipes`
- `/meals`

Documentación interactiva en `http://localhost:8000/docs` y en `http://localhost:8000/redoc`.

---

## 4. Frontend Interactivo con Streamlit

`app.py` proporciona una interfaz visual para interactuar con la API REST. Ofrece secciones para:

- Gestión de alimentos
- Gestión de recetas
- Planificador de comidas

Ejecutar con:

```bash
streamlit run app.py
```

---

## 5. Cómo Ejecutar el Proyecto completo

Aunque es una mala prácitoca, he subido el .venv para facilitar la ejecución del proyecto.
Desde la raíz del proyecto:

```bash
.venv\Scripts\activate
uvicorn api:app --reload
streamlit run app.py
```

Ver en `http://localhost:8501`

---

## 6. Funcionalidades Clave

- 📥 Scraping automatizado de datos nutricionales.
- 🧠 Cálculo automático de nutrientes en recetas y comidas.
- 🧾 CRUD de alimentos, recetas y comidas.
- 📊 Análisis y resumen de nutrientes diarios/semanales.
- 📅 Calendario interactivo de planificación alimentaria.

