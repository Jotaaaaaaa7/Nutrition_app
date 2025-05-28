import requests
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from Food_section import seccion_alimentos
from Recipes_section import seccion_recetas
from Planner_section import seccion_planificador




# Configuración de la página (DEBE SER LO PRIMERO)
st.set_page_config(
    page_title="Nutrición App",
    page_icon="🥗",
    layout="wide"
)




def main():
    # Inicialización del estado de la sesión
    if 'seccion_actual' not in st.session_state:
        st.session_state.seccion_actual = "Planificador"
    if 'mostrar_form_alimento' not in st.session_state:
        st.session_state.mostrar_form_alimento = False
    if 'mostrar_form_receta' not in st.session_state:
        st.session_state.mostrar_form_receta = False
    if 'mostrar_form_comida' not in st.session_state:
        st.session_state.mostrar_form_comida = False
    if 'fecha_planificador' not in st.session_state:
        st.session_state.fecha_planificador = date.today()

    # Barra lateral para navegación (SOLO AQUÍ, eliminar la otra implementación)
    with st.sidebar:
        st.title("Nutrición App 🥗")
        st.subheader("Navegación")

        if st.button("Planificador", use_container_width=True,
                   type="primary" if st.session_state.seccion_actual == "Planificador" else "secondary",
                   key="btn_planificador_nav"):  # Añadir key única
            st.session_state.seccion_actual = "Planificador"
            st.rerun()

        if st.button("Alimentos", use_container_width=True,
                   type="primary" if st.session_state.seccion_actual == "Alimentos" else "secondary",
                   key="btn_alimentos_nav"):  # Añadir key única
            st.session_state.seccion_actual = "Alimentos"
            st.rerun()

        if st.button("Recetas", use_container_width=True,
                   type="primary" if st.session_state.seccion_actual == "Recetas" else "secondary",
                   key="btn_recetas_nav"):  # Añadir key única
            st.session_state.seccion_actual = "Recetas"
            st.rerun()


    # Renderizar la sección actual según la selección
    if st.session_state.seccion_actual == "Alimentos":
        seccion_alimentos()
    elif st.session_state.seccion_actual == "Recetas":
        seccion_recetas()
    # elif st.session_state.seccion_actual == "Comidas":
    #     seccion_comidas()
    elif st.session_state.seccion_actual == "Planificador":
        seccion_planificador()

if __name__ == "__main__":
    main()