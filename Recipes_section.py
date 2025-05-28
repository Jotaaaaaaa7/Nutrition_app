import requests
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from typing import List, Optional
from frontend_utils import fetch_data, post_data, update_data, delete_data, clear_caches


# Sección: Recetas
def seccion_recetas():
    # Título principal con estilo mejorado y emoji
    st.markdown("""
    <h1 style='color: #FF9F46; text-align: center; margin-bottom: 20px;'>
        🍽️ Gestión de Recetas
    </h1>
    """, unsafe_allow_html=True)

    # Inicializar variables de estado
    if 'ingredientes_temp' not in st.session_state:
        st.session_state.ingredientes_temp = []
    if 'editar_receta' not in st.session_state:
        st.session_state.editar_receta = None
    if 'mostrar_form_receta' not in st.session_state:
        st.session_state.mostrar_form_receta = False

    # Obtener recetas y alimentos de la API
    recetas = fetch_data("/recipes")
    alimentos = fetch_data("/foods")

    # Control de mostrar/ocultar formulario
    if st.session_state.mostrar_form_receta:
        # Determinar si estamos en modo edición o creación
        receta_editar = None
        if st.session_state.editar_receta:
            # Buscar la receta a editar
            for r in recetas:
                if r['id'] == st.session_state.editar_receta:
                    receta_editar = r
                    break

            if not receta_editar:
                st.error("No se encontró la receta seleccionada.")
                st.session_state.editar_receta = None
                st.session_state.mostrar_form_receta = False
                st.rerun()

        # Contenedor principal para el formulario con borde y estilo
        with st.container(border=True):
            # Título según el modo con estilo mejorado
            if receta_editar:
                st.markdown(f"""
                <h2 style='color: #4CAF50; margin-bottom: 15px;'>
                    ✏️ Editar receta: {receta_editar['name']}
                </h2>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <h2 style='color: #4CAF50; margin-bottom: 15px;'>
                    ➕ Crear nueva receta
                </h2>
                """, unsafe_allow_html=True)
                # Solo limpiar los ingredientes al iniciar el formulario por primera vez
                if 'ingredientes_temp' in st.session_state and 'iniciar_nueva_receta' not in st.session_state:
                    st.session_state.ingredientes_temp = []
                    st.session_state.iniciar_nueva_receta = True

            # Mostrar formulario (mismo para crear y editar)
            resultado = formulario_receta(alimentos, receta_editar)

            # Procesar resultado del formulario
            if resultado is not None:
                if receta_editar:
                    # Actualizar receta existente
                    if update_data(f"/recipes/{resultado['receta_id']}", resultado['data']):
                        st.toast(f"✅ Receta '{resultado['data']['name']}' actualizada correctamente", icon="✅")
                        # Mantenemos el formulario visible pero actualizamos las cachés
                        clear_caches()
                        # Mantenemos el modo de edición
                else:
                    # Crear nueva receta
                    if post_data("/recipes", resultado['data']):
                        st.toast(f"✅ Receta '{resultado['data']['name']}' creada correctamente", icon="✅")
                        # Limpiamos los ingredientes para una nueva receta
                        st.session_state.ingredientes_temp = []
                        st.session_state.iniciar_nueva_receta = False
                        clear_caches()
                        # Mantenemos el formulario abierto para crear otra receta
                        st.rerun()

            # Botón para cancelar con margen superior
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("❌ Salir", use_container_width=True, key="btn_cancelar_receta", type="secondary"):
                st.session_state.mostrar_form_receta = False
                st.session_state.editar_receta = None
                st.rerun()
    else:
        # Mostrar lista de recetas cuando no se está editando/creando
        # Panel superior con título y botón de nueva receta
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("""
                <h3 style='color: #64B5F6; margin: 10px 0;'>
                    📋 Recetas disponibles
                </h3>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("➕ Nueva receta", type="primary", use_container_width=True, key="btn_nueva_receta"):
                    # Activar modo de creación
                    st.session_state.mostrar_form_receta = True
                    st.session_state.editar_receta = None
                    st.rerun()

        # Lista de recetas
        if not recetas:
            # Mensaje mejorado cuando no hay recetas
            st.markdown("""
            <div style='background-color: rgba(100, 181, 246, 0.1); padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;'>
                <p style='margin: 0; font-size: 16px;'>🍽️ No hay recetas registradas. ¡Crea tu primera receta!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Contenedor para lista de recetas con espacio superior
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            for i, receta in enumerate(recetas):
                with st.expander(f"🍳 {receta['name']} - {len(receta['ingredients'])} ingredientes"):
                    # Columnas para información con mejor espaciado
                    col_info, col_nutr = st.columns([2, 2], gap='large')

                    with col_info:
                        # Mostrar ingredientes en tabla con título mejorado
                        st.markdown("##### 📝 Ingredientes:")
                        # Crear dataframe de ingredientes
                        ingredientes_data = {
                            "Ingrediente": [ing['food_name'] for ing in receta['ingredients']],
                            "Cantidad (g)": [ing['quantity_g'] for ing in receta['ingredients']]
                        }
                        ingredientes_df = pd.DataFrame(ingredientes_data)
                        st.dataframe(ingredientes_df, use_container_width=True, hide_index=True)

                        # Descripción con estilo mejorado
                        if receta['description']:
                            st.markdown(f"""
                            <div style='background-color: rgba(100, 100, 100, 0.1); padding: 10px; border-radius: 5px; margin-top: 10px;'>
                                <em>{receta['description']}</em>
                            </div>
                            """, unsafe_allow_html=True)

                    with col_nutr:
                        # Información nutricional en tabla con título mejorado
                        st.markdown("##### 📊 Información Nutricional:")
                        # Crear dataframe de nutrientes
                        nutrientes_data = {
                            "Nutriente": ["🔥 Calorías", "🥩 Proteínas", "🍚 Carbohidratos", "🧈 Grasas"],
                            "Valor": [
                                f"{receta['nutrients']['kcal']:.0f} kcal",
                                f"{receta['nutrients']['protein_g']:.1f} g",
                                f"{receta['nutrients']['carbs_g']:.1f} g",
                                f"{receta['nutrients']['fat_g']:.1f} g"
                            ]
                        }
                        nutrientes_df = pd.DataFrame(nutrientes_data)
                        st.dataframe(nutrientes_df, use_container_width=True, hide_index=True)

                    # Separador visual antes de botones
                    st.markdown("<hr style='margin: 15px 0 10px 0; opacity: 0.3;'>", unsafe_allow_html=True)

                    # Botones de acción con mejor disposición
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✏️ Editar", key=f"edit_receta_{i}", use_container_width=True):
                            st.session_state.mostrar_form_receta = True
                            st.session_state.editar_receta = receta['id']
                            st.rerun()
                    with col_b:
                        if st.button("🗑️ Eliminar", key=f"del_receta_{i}", use_container_width=True):
                            if delete_data(f"/recipes/{receta['id']}"):
                                st.toast(f"✅ Receta '{receta['name']}' eliminada correctamente", icon="✅")
                                clear_caches()
                                st.rerun()


def mostrar_lista_recetas(recetas):
    """Muestra la lista de recetas disponibles"""
    # Contenedor principal con borde para el encabezado
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("""
            <h3 style='color: #64B5F6; margin: 10px 0;'>
                📋 Recetas disponibles
            </h3>
            """, unsafe_allow_html=True)
        with col2:
            st.button("➕ Nueva receta", type="primary", use_container_width=True, key="btn_nueva_receta_lista",
                     on_click=lambda: setattr(st.session_state, 'mostrar_form_receta', True))

    # Lista de recetas
    if not recetas:
        # Mensaje mejorado cuando no hay recetas
        st.markdown("""
        <div style='background-color: rgba(100, 181, 246, 0.1); padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;'>
            <p style='margin: 0; font-size: 16px;'>🍽️ No hay recetas registradas. ¡Crea tu primera receta!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Contenedor con scroll para lista de recetas
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        with st.container():
            for i, receta in enumerate(recetas):
                with st.expander(f"🍳 {receta['name']} - {len(receta['ingredients'])} ingredientes"):
                    # Columnas para información con mejor espaciado
                    col_info, col_nutr = st.columns([3, 2])

                    with col_info:
                        # Mostrar ingredientes con estilo mejorado
                        st.markdown("##### 📝 Ingredientes:")

                        # Lista de ingredientes con mejor formato
                        ing_html = ""
                        for ing in receta['ingredients']:
                            ing_html += f"<li><b>{ing['food_name']}</b>: {ing['quantity_g']} g</li>"

                        st.markdown(f"""
                        <ul style='margin-top: 5px; padding-left: 20px;'>
                            {ing_html}
                        </ul>
                        """, unsafe_allow_html=True)

                        # Descripción con estilo mejorado
                        if receta['description']:
                            st.markdown(f"""
                            <div style='background-color: rgba(100, 100, 100, 0.1); padding: 10px; border-radius: 5px; margin-top: 10px;'>
                                <em>{receta['description']}</em>
                            </div>
                            """, unsafe_allow_html=True)

                    with col_nutr:
                        # Información nutricional resumida con título mejorado
                        st.markdown("##### 📊 Información Nutricional:")
                        # Valores con mejor estilo visual usando st.metric
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("🔥 Calorías", f"{receta['nutrients']['kcal']:.0f} kcal")
                            st.metric("🥩 Proteínas", f"{receta['nutrients']['protein_g']:.1f} g")
                        with col_b:
                            st.metric("🍚 Carbos", f"{receta['nutrients']['carbs_g']:.1f} g")
                            st.metric("🧈 Grasas", f"{receta['nutrients']['fat_g']:.1f} g")

                    # Separador visual antes de botones
                    st.markdown("<hr style='margin: 15px 0 10px 0; opacity: 0.3;'>", unsafe_allow_html=True)

                    # Botones de acción mejorados
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✏️ Editar", key=f"edit_receta_lista_{i}", use_container_width=True):
                            st.session_state.editar_receta = receta['id']
                            st.session_state.mostrar_form_receta = True
                            st.rerun()
                    with col_b:
                        if st.button("🗑️ Eliminar", key=f"del_receta_lista_{i}", use_container_width=True):
                            if delete_data(f"/recipes/{receta['id']}"):
                                st.toast(f"✅ Receta '{receta['name']}' eliminada correctamente", icon="✅")
                                clear_caches()
                                st.rerun()


def formulario_receta(alimentos, receta_editar=None):
    """
    Muestra un formulario para crear o editar una receta.

    Args:
        alimentos: Lista de alimentos disponibles
        receta_editar: Receta existente para editar (None para nueva receta)

    Returns:
        dict: Datos de la receta o None si se cancela
    """
    # Determinar si estamos en modo edición
    editar_modo = receta_editar is not None

    # Inicializar ingredientes si no existen
    if 'ingredientes_temp' not in st.session_state:
        if editar_modo and receta_editar and 'ingredients' in receta_editar:
            st.session_state.ingredientes_temp = [
                {"alimento": ing["food_name"], "cantidad": ing["quantity_g"]}
                for ing in receta_editar['ingredients']
            ]
        else:
            st.session_state.ingredientes_temp = []

    # Título guía según el modo
    if editar_modo:
        st.markdown("""
        <div style='background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <p style='margin: 0;'>📝 Modifica los detalles de la receta y sus ingredientes</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <p style='margin: 0;'>📝 Completa los detalles de la receta y añade ingredientes</p>
        </div>
        """, unsafe_allow_html=True)

    # Formulario con columnas para aprovechar espacio
    col_izq, col_der = st.columns([1, 1])

    # Columna izquierda: Datos básicos de la receta
    with col_izq:
        with st.container(border=True):
            st.markdown("##### 📌 Detalles básicos")
            nombre_receta = st.text_input(
                "Nombre de la receta",
                value=receta_editar['name'] if receta_editar else "",
                placeholder="Introduce un nombre descriptivo"
            )

            descripcion = st.text_area(
                "Descripción",
                value=receta_editar['description'] if receta_editar else "",
                placeholder="Describe brevemente la receta...",
                height=100
            )

    # Columna derecha: Selector de ingredientes
    with col_der:
        with st.container(border=True, height=245):
            st.markdown("##### 🥕 Añadir ingredientes")
            if alimentos:
                # Diseño con tres columnas en lugar de dos
                col1, col2, col3 = st.columns([3, 1.8, 0.8])

                with col1:
                    opciones_alimentos = [food["name"] for food in alimentos]
                    alimento_sel = st.selectbox("Selecciona un alimento", opciones_alimentos)

                    # Obtener el alimento seleccionado completo
                    alimento_completo = next((food for food in alimentos if food["name"] == alimento_sel), None)

                    # Determinar el step según el valor de unit del alimento
                    step_valor = 5.0  # Valor predeterminado (convertido a float)
                    if alimento_completo and alimento_completo.get("unit") is not None:
                        step_valor = float(alimento_completo["unit"])

                # Inicializar variables para gestionar el contador del botón
                if "btn_cantidad_count" not in st.session_state:
                    st.session_state.btn_cantidad_count = 0

                # Inicializar valor de cantidad actual
                if "cantidad_actual" not in st.session_state:
                    st.session_state.cantidad_actual = float(step_valor) if step_valor > 1 else 100.0

                with col2:
                    cat = alimento_completo["category"]
                    if cat == 'Aceites y grasas':
                        txt = "Cucharada/s"
                    elif cat == 'Bebidas':
                        txt = "Vasos/s"
                    elif cat in ['Frutas', 'Verduras y hortalizas']:
                        txt = "Pieza/s"
                    else:
                        txt = ''

                    cantidad = st.number_input(
                        "Cantidad (g)",
                        min_value=1.0,
                        step=step_valor,
                        value=st.session_state.cantidad_actual,
                        key=f"input_cantidad_{st.session_state.btn_cantidad_count}",
                        help="Cantidad en gramos del alimento seleccionado"
                    )
                    # Actualizar el valor en session_state
                    st.session_state.cantidad_actual = cantidad

                    # Mostrar equivalencia
                    if txt:
                        st.markdown(f'{round(cantidad/step_valor, 1)} {txt}')

                # Columna para el botón "+1/2"
                with col3:
                    # Agregar espacio para alinear con el campo de entrada
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Determinar si el botón debe estar activo
                    boton_disabled = not (alimento_completo and alimento_completo.get("unit") is not None)

                    if st.button("+1/2",
                               disabled=boton_disabled,
                               use_container_width=True,
                               key=f"btn_medio_{st.session_state.btn_cantidad_count}"):
                        if not boton_disabled:
                            # Calcular la mitad del valor de unidad
                            medio_step = float(alimento_completo["unit"]) / 2
                            # Incrementar el valor
                            st.session_state.cantidad_actual += medio_step
                            # Actualizar contador para forzar recreación
                            st.session_state.btn_cantidad_count += 1
                            st.rerun()

                if st.button("➕ Añadir ingrediente",
                           disabled=not alimento_sel,
                           use_container_width=True,
                           key="btn_add_ingrediente",
                           type="primary"):
                    if alimento_sel:
                        # Verificar si el alimento ya existe en la lista
                        alimento_existe = False
                        for i, ing in enumerate(st.session_state.ingredientes_temp):
                            if ing["alimento"] == alimento_sel:
                                # Actualizar la cantidad si el alimento ya existe
                                st.session_state.ingredientes_temp[i]["cantidad"] = cantidad
                                alimento_existe = True
                                break

                        # Agregar solo si es un nuevo alimento
                        if not alimento_existe:
                            st.session_state.ingredientes_temp.append({
                                "alimento": alimento_sel,
                                "cantidad": cantidad
                            })
                        st.rerun()
            else:
                st.warning("No hay alimentos disponibles. Añade alimentos primero.")

    # Lista de ingredientes añadidos
    if st.session_state.ingredientes_temp:
        # Calculamos nutrientes por ingrediente y totales
        ingredientes_con_nutrientes = []
        total_nutrientes = {
            "kcal": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0
        }

        # Procesar cada ingrediente
        for ing in st.session_state.ingredientes_temp:
            alimento_nombre = ing["alimento"]
            cantidad = ing["cantidad"]

            # Buscar el alimento en la lista
            alimento_data = next((a for a in alimentos if a["name"] == alimento_nombre), None)

            # Calcular nutrientes
            nutrientes = {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

            if alimento_data and "nutrients" in alimento_data:
                # Factor de proporción según cantidad (nutrientes son por 100g)
                factor = cantidad / 100

                # Calcular nutrientes para esta cantidad
                nutrientes = {
                    "kcal": alimento_data["nutrients"]["kcal"] * factor,
                    "protein_g": alimento_data["nutrients"]["protein_g"] * factor,
                    "carbs_g": alimento_data["nutrients"]["carbs_g"] * factor,
                    "fat_g": alimento_data["nutrients"]["fat_g"] * factor
                }

            # Agregar a totales
            for key in total_nutrientes:
                total_nutrientes[key] += nutrientes[key]

            # Agregar a lista con nutrientes
            ingredientes_con_nutrientes.append({
                "alimento": alimento_nombre,
                "cantidad": cantidad,
                "kcal": round(nutrientes["kcal"], 1),
                "proteina": round(nutrientes["protein_g"], 1),
                "carbos": round(nutrientes["carbs_g"], 1),
                "grasas": round(nutrientes["fat_g"], 1)
            })

        # Crear dataframe de ingredientes con nutrientes
        ingredientes_data = {
            "Alimento": [ing["alimento"] for ing in ingredientes_con_nutrientes],
            "Cantidad (g)": [ing["cantidad"] for ing in ingredientes_con_nutrientes],
            "Kcal": [ing["kcal"] for ing in ingredientes_con_nutrientes],
            "Prot (g)": [ing["proteina"] for ing in ingredientes_con_nutrientes],
            "Carbs (g)": [ing["carbos"] for ing in ingredientes_con_nutrientes],
            "Grasas (g)": [ing["grasas"] for ing in ingredientes_con_nutrientes]
        }
        ingredientes_df = pd.DataFrame(ingredientes_data)

        # Crear dataframe para resumen nutricional
        resumen_data = {
            "Nutriente": ["🔥 Calorías", "🥩 Proteínas", "🍚 Carbohidratos", "🧈 Grasas"],
            "Valor": [
                f"{total_nutrientes['kcal']:.0f} kcal",
                f"{total_nutrientes['protein_g']:.1f} g",
                f"{total_nutrientes['carbs_g']:.1f} g",
                f"{total_nutrientes['fat_g']:.1f} g"
            ]
        }
        resumen_df = pd.DataFrame(resumen_data)

        # Título mejorado para la tabla de ingredientes
        st.markdown("""
        <h5 style='margin-top: 20px; margin-bottom: 10px; color: #64B5F6;'>
            📋 Resumen de ingredientes y nutrientes
        </h5>
        """, unsafe_allow_html=True)

        # Layout con columnas (tabla principal, botones, resumen nutricional)
        col1, col_resumen = st.columns([2, 1])

        with col1:
            # Mostrar tabla con borde y estilo
            with st.container(border=True, height=380):
                col_tabla, col_eliminar = st.columns([2, 1])

                with col_tabla:
                    st.markdown("##### 📝 Ingredientes añadidos:")
                    st.dataframe(
                        ingredientes_df,
                        use_container_width=True,
                        height=300,
                        hide_index=True,
                        column_config={
                            "Alimento": st.column_config.TextColumn("Alimento"),
                            "Cantidad (g)": st.column_config.NumberColumn("Cantidad (g)", format="%d g"),
                            "Kcal": st.column_config.NumberColumn("Kcal", format="%.1f"),
                            "Prot (g)": st.column_config.NumberColumn("Prot (g)", format="%.1f"),
                            "Carbs (g)": st.column_config.NumberColumn("Carbs (g)", format="%.1f"),
                            "Grasas (g)": st.column_config.NumberColumn("Grasas (g)", format="%.1f"),
                        }
                    )

                with col_eliminar:
                    st.markdown("##### 🗑️ Gestionar ingredientes")
                    indice_eliminar = st.selectbox(
                        "Selecciona ingrediente:",
                        options=range(len(st.session_state.ingredientes_temp)),
                        format_func=lambda i: f"{ingredientes_df.iloc[i]['Alimento']} ({ingredientes_df.iloc[i]['Cantidad (g)']}g)",
                        key="select_eliminar_ingrediente"
                    )

                    if st.button("🗑️ Eliminar seleccionado", key="btn_eliminar_ingrediente", use_container_width=True):
                        if indice_eliminar is not None:
                            st.session_state.ingredientes_temp.pop(indice_eliminar)
                            st.rerun()

        # Nueva columna para el resumen nutricional
        with col_resumen:
            with st.container(border=True):
                st.markdown("##### 📊 Información Nutricional:")
                st.dataframe(
                    resumen_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Nutriente": st.column_config.TextColumn("Nutriente"),
                        "Valor": st.column_config.TextColumn("Valor"),
                    }
                )

                # Botones de acción con mejor disposición
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("🧹 Limpiar ingredientes", use_container_width=True, key="btn_limpiar_ingredientes"):
                    st.session_state.ingredientes_temp = []
                    st.rerun()

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("💾 Guardar receta", type="primary", use_container_width=True, key="btn_guardar_receta"):
                    if nombre_receta and st.session_state.ingredientes_temp:
                        # Construir el objeto de receta
                        recipe_data = {
                            "name": nombre_receta,
                            "description": descripcion,
                            "ingredient_quantities": {
                                ing["alimento"]: ing["cantidad"]
                                for ing in st.session_state.ingredientes_temp
                            }
                        }

                        # Retornar los datos y la receta_id si estamos editando
                        return {
                            "data": recipe_data,
                            "receta_id": receta_editar['id'] if editar_modo else None
                        }
                    else:
                        st.error("Debes especificar un nombre y añadir al menos un ingrediente")

    else:
        # Mensaje mejorado cuando no hay ingredientes
        st.markdown("""
        <div style='background-color: rgba(255, 193, 7, 0.1); padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;'>
            <p style='margin: 0;'>⚠️ Aún no has añadido ingredientes</p>
            <p style='margin: 5px 0 0 0; font-size: 0.9em;'>Selecciona alimentos y sus cantidades para comenzar</p>
        </div>
        """, unsafe_allow_html=True)

    # if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_formulario"):
    #     # Al cancelar, simplemente limpiar los ingredientes temporales
    #     st.session_state.ingredientes_temp = []
    #     return None

    return None


