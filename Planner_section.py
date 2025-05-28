import requests
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from typing import List, Optional
from frontend_utils import fetch_data, post_data, update_data, delete_data, clear_caches


def seccion_planificador():
    # Título mejorado con estilo visual y espaciado
    st.markdown("""
    <h1 style='color:#64B5F6; margin-bottom:0.5em; display:flex; align-items:center; gap:10px;'>
        <span>📆</span> <span>Planificador de Comidas</span>
    </h1>
    <hr style='margin:0.5em 0 1.5em 0; border-color:rgba(255,255,255,0.2);'>
    """, unsafe_allow_html=True)

    # Inicializar variables de estado
    if 'fecha_planificador' not in st.session_state:
        st.session_state.fecha_planificador = date.today()
    if 'mostrar_form_comida_planificador' not in st.session_state:
        st.session_state.mostrar_form_comida_planificador = False
    if 'editar_comida_planificador' not in st.session_state:
        st.session_state.editar_comida_planificador = None

    # Cargar datos desde la API
    comidas = fetch_data("/meals") or []
    recetas = fetch_data("/recipes") or []
    alimentos = fetch_data("/foods") or []

    # Diccionarios para búsquedas rápidas
    food_dict = {a['id']: a['name'] for a in alimentos}
    recipe_dict = {r['id']: r['name'] for r in recetas}

    def get_food_name(food_id):
        return food_dict.get(food_id, f"Alimento #{food_id}")

    def get_recipe_name(recipe_id):
        return recipe_dict.get(recipe_id, f"Receta #{recipe_id}")

    # Crear un conjunto con fechas que tienen comidas
    fechas_con_comidas = {c.get('meal_date') for c in comidas if c.get('meal_date')}

    # Si estamos en modo formulario, mostrar el formulario y salir
    if st.session_state.mostrar_form_comida_planificador:
        # Determinar si estamos en modo edición
        comida_existente = None
        if st.session_state.editar_comida_planificador:
            comida_existente = next((c for c in comidas if c['id'] == st.session_state.editar_comida_planificador),
                                    None)

        # Pasar la fecha actual seleccionada al formulario
        fecha_actual = st.session_state.fecha_planificador

        # Mostrar formulario y procesar resultado
        resultado = formulario_comida(fecha_actual, recetas, alimentos, comida_existente)

        if resultado is not None:
            # Procesar el formulario enviado
            if st.session_state.editar_comida_planificador:
                # Actualizar comida existente
                if update_data(f"/meals/{st.session_state.editar_comida_planificador}", resultado):
                    st.success("Comida actualizada correctamente")
                else:
                    st.error("Error al actualizar la comida")
            else:
                # Crear nueva comida
                if post_data("/meals", resultado):
                    st.success("Comida creada correctamente")
                else:
                    st.error("Error al crear la comida")

            # Limpiar estado y actualizar caché
            st.session_state.mostrar_form_comida_planificador = False
            st.session_state.editar_comida_planificador = None
            clear_caches()
            st.rerun()

        # El botón de cancelar ya está dentro del formulario
        return

    # ===================== PANEL PRINCIPAL DE NAVEGACIÓN =====================
    fecha_actual = st.session_state.fecha_planificador
    lunes = fecha_actual - timedelta(days=fecha_actual.weekday())

    # Contenedor mejorado con borde para la navegación del calendario
    with st.container(border=True):
        st.markdown("""
        <h4 style='margin-top:0; margin-bottom:10px; color:#64B5F6; font-size:1.1em;'>
            📅 Navegación del calendario
        </h4>
        """, unsafe_allow_html=True)

        # Panel superior - Calendario y navegación
        col_izq, col_central, col_der = st.columns([1, 10, 1])

        # Columna izquierda: navegación entre semanas - botón mejorado
        with col_izq:
            if st.button("◀",
                         use_container_width=True,
                         help="Semana anterior"):  # Tooltip añadido
                st.session_state.fecha_planificador = fecha_actual - timedelta(days=7)
                st.rerun()

        # Columna central: selector de fecha y mini-calendario
        with col_central:
            # Selector de fecha con mejor estilo
            fecha_seleccionada = st.date_input(
                "Selecciona fecha",
                value=fecha_actual,
                key="fecha_principal",
                help="Selecciona la fecha para ver o crear comidas"  # Tooltip informativo
            )
            if fecha_seleccionada != fecha_actual:
                st.session_state.fecha_planificador = fecha_seleccionada
                st.rerun()

            # Mini-calendario semanal mejorado con contenedor
            st.markdown("<div style='margin-top:10px; margin-bottom:5px;'></div>", unsafe_allow_html=True)

            dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
            cols_semana = st.columns(7)

            for i, dia in enumerate(dias_semana):
                fecha_dia = lunes + timedelta(days=i)
                fecha_iso = fecha_dia.isoformat()

                # Determinar el estado visual del día
                es_seleccionado = fecha_dia == fecha_actual
                hay_comidas = fecha_iso in fechas_con_comidas

                # Mejora visual con emojis más distinguibles
                emoji = "⚫"  # Por defecto: sin seleccionar y sin comidas
                if es_seleccionado and hay_comidas:
                    emoji = "🟢"  # Verde: seleccionado con comidas
                elif es_seleccionado:
                    emoji = "⚪"  # Blanco: seleccionado sin comidas
                elif hay_comidas:
                    emoji = "🔵"  # Azul: con comidas

                with cols_semana[i]:
                    # Botón de día con estilo mejorado
                    if st.button(f"{emoji}\n{dia}\n{fecha_dia.day}",
                                 key=f"day_{i}",
                                 use_container_width=True,
                                 help=f"Ver {fecha_dia.strftime('%d/%m/%Y')}"):  # Tooltip con fecha completa
                        st.session_state.fecha_planificador = fecha_dia
                        st.rerun()

        # Columna derecha: navegación entre semanas - botón mejorado
        with col_der:
            if st.button("▶",
                         use_container_width=True,
                         help="Semana siguiente"):  # Tooltip añadido
                st.session_state.fecha_planificador = fecha_actual + timedelta(days=7)
                st.rerun()

    # Espaciado mejorado entre secciones
    st.markdown("<div style='margin:15px 0;'></div>", unsafe_allow_html=True)

    # ===================== CONTENIDO PRINCIPAL =====================
    # Pestañas con estilo mejorado
    tab_dia, tab_semana = st.tabs(["📅 Vista diaria", "📆 Vista semanal"])

    # ---- TAB: VISTA DIARIA ----
    with tab_dia:
        # Botón de crear comida mejorado con margen
        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
        if st.button("✨ Crear comida",
                     type="primary",
                     use_container_width=True,
                     key='crear_comida',
                     help="Añade una nueva comida para esta fecha"):  # Tooltip añadido
            st.session_state.mostrar_form_comida_planificador = True
            st.rerun()

        fecha_iso = fecha_actual.isoformat()
        comidas_fecha = [c for c in comidas if c.get('meal_date') == fecha_iso]

        # Título de la fecha con mejor formato
        st.markdown(f"""
        <h2 style='margin-top:20px; color:#64B5F6; font-size:1.5em;'>
            Comidas para: {fecha_actual.strftime('%d/%m/%Y')}
        </h2>
        """, unsafe_allow_html=True)

        # Mostrar comidas del día o mensaje vacío
        if comidas_fecha:
            # Inicializar totales nutricionales del día
            total_nutrients = {
                "kcal": 0, "protein_g": 0, "carbs_g": 0,
                "fat_g": 0
            }

            # Mostrar cada comida en una tarjeta mejorada
            for comida in comidas_fecha:
                # Expander mejorado con información visual en el título
                with st.expander(
                        f"🍽️ Comida #{comida['id']} - {sum(1 for i in comida['items'] if i['component_type'] == 'recipe')} recetas · {comida['nutrients']['kcal']:.0f} kcal",
                        expanded=True
                ):
                    # Contenedor con borde para mejorar la presentación
                    with st.container(border=True):
                        col1, col2 = st.columns([4, 1], gap='large')

                        with col1:
                            # TABLA UNIFICADA PARA RECETAS Y ALIMENTOS
                            st.markdown("""
                            <p style='margin-bottom:10px; font-weight:500; color:#64B5F6;'>
                                📋 Componentes de la comida:
                            </p>
                            """, unsafe_allow_html=True)

                            # Preparar datos unificados
                            componentes_data = []

                            # Procesar recetas
                            recetas_items = [item for item in comida["items"] if item["component_type"] == "recipe"]
                            for item in recetas_items:
                                receta_id = item['component_id']
                                receta_nombre = get_recipe_name(receta_id)
                                receta_completa = fetch_data(f"/recipes/{receta_id}")

                                if receta_completa:
                                    # Crear texto resumido de ingredientes
                                    ingredientes_texto = ""
                                    if "ingredients" in receta_completa and receta_completa["ingredients"]:
                                        ingredientes_lista = []
                                        for ingrediente in receta_completa["ingredients"][:3]:
                                            if "food_name" in ingrediente and "quantity_g" in ingrediente:
                                                ing_nombre = ingrediente["food_name"]
                                                ing_cantidad = ingrediente["quantity_g"]
                                                ingredientes_lista.append(f"{ing_nombre} ({ing_cantidad}g)")

                                        ingredientes_texto = ", ".join(ingredientes_lista)
                                        total_ingredientes = len(receta_completa["ingredients"])
                                        if total_ingredientes > 3:
                                            ingredientes_texto += "..."

                                    if not ingredientes_texto:
                                        ingredientes_texto = "Sin datos de ingredientes"

                                    componentes_data.append({
                                        "Tipo": "🍽️ Receta",
                                        "Nombre": receta_nombre,
                                        "Detalles": ingredientes_texto,
                                        "Cantidad": "",
                                        "Kcal": f"{receta_completa.get('nutrients', {}).get('kcal', 0):.0f}",
                                        "Prot": f"{receta_completa.get('nutrients', {}).get('protein_g', 0):.1f} g",
                                        "Carbos": f"{receta_completa.get('nutrients', {}).get('carbs_g', 0):.1f} g",
                                        "Grasas": f"{receta_completa.get('nutrients', {}).get('fat_g', 0):.1f} g"
                                    })

                            # Procesar alimentos adicionales
                            alimentos_items = [item for item in comida["items"] if item["component_type"] == "food"]
                            for item in alimentos_items:
                                alimento_nombre = get_food_name(item['component_id'])
                                cantidad = item['quantity']
                                alimento_completo = next((a for a in alimentos if a['id'] == item['component_id']),
                                                         None)

                                if alimento_completo and "nutrients" in alimento_completo:
                                    factor = cantidad / 100
                                    componentes_data.append({
                                        "Tipo": "🥗 Alimento",
                                        "Nombre": alimento_nombre,
                                        "Detalles": "-",
                                        "Cantidad": f"{cantidad} g",
                                        "Kcal": f"{alimento_completo['nutrients']['kcal'] * factor:.0f}",
                                        "Prot": f"{alimento_completo['nutrients']['protein_g'] * factor:.1f} g",
                                        "Carbos": f"{alimento_completo['nutrients']['carbs_g'] * factor:.1f} g",
                                        "Grasas": f"{alimento_completo['nutrients']['fat_g'] * factor:.1f} g"
                                    })

                            # Mostrar tabla unificada con mejor estilo
                            if componentes_data:
                                df_componentes = pd.DataFrame(componentes_data)
                                st.dataframe(
                                    df_componentes,
                                    use_container_width=True,
                                    hide_index=True,
                                    height=None if len(componentes_data) <= 6 else 285,
                                    column_config={  # Configuración mejorada de columnas
                                        "Tipo": st.column_config.TextColumn("Tipo"),
                                        "Nombre": st.column_config.TextColumn("Nombre"),
                                        "Detalles": st.column_config.TextColumn("Detalles"),
                                        "Cantidad": st.column_config.TextColumn("Cantidad"),
                                        "Kcal": st.column_config.TextColumn("Kcal"),
                                        "Prot": st.column_config.TextColumn("Prot"),
                                        "Carbos": st.column_config.TextColumn("Carbos"),
                                        "Grasas": st.column_config.TextColumn("Grasas"),
                                    }
                                )
                            else:
                                # Mensaje de información mejorado
                                st.markdown("""
                                <div style='background-color:rgba(100,181,246,0.1); padding:15px; border-radius:5px; text-align:center;'>
                                    <p style='margin:0; color:#64B5F6;'>ℹ️ Esta comida no tiene componentes registrados</p>
                                </div>
                                """, unsafe_allow_html=True)

                        with col2:
                            # Contenedor visual para nutrientes
                            st.markdown("""
                            <p style='margin-bottom:10px; font-weight:500; color:#64B5F6;'>
                                📊 Información nutricional:
                            </p>
                            """, unsafe_allow_html=True)

                            # Mostrar cada valor nutricional con estilo mejorado
                            st.markdown(f"""
                            <div style='background-color:rgba(255,152,0,0.1); padding:8px; border-radius:5px; margin-bottom:5px;'>
                                <p style='margin:0; display:flex; justify-content:space-between;'>
                                    <span>🔥 Calorías:</span> <strong>{comida['nutrients']['kcal']:.0f} kcal</strong>
                                </p>
                            </div>
                            <div style='background-color:rgba(233,30,99,0.1); padding:8px; border-radius:5px; margin-bottom:5px;'>
                                <p style='margin:0; display:flex; justify-content:space-between;'>
                                    <span>🥩 Proteína:</span> <strong>{comida['nutrients']['protein_g']:.1f} g</strong>
                                </p>
                            </div>
                            <div style='background-color:rgba(3,169,244,0.1); padding:8px; border-radius:5px; margin-bottom:5px;'>
                                <p style='margin:0; display:flex; justify-content:space-between;'>
                                    <span>🍚 Carbohidratos:</span> <strong>{comida['nutrients']['carbs_g']:.1f} g</strong>
                                </p>
                            </div>
                            <div style='background-color:rgba(0,150,136,0.1); padding:8px; border-radius:5px; margin-bottom:10px;'>
                                <p style='margin:0; display:flex; justify-content:space-between;'>
                                    <span>🧈 Grasas:</span> <strong>{comida['nutrients']['fat_g']:.1f} g</strong>
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Botones de acción con mejor alineación
                            col_edit, col_delete = st.columns(2)

                            with col_edit:
                                if st.button("✏️ Editar",
                                             key=f"edit_{comida['id']}",
                                             use_container_width=True,
                                             help="Editar esta comida"):  # Tooltip añadido
                                    st.session_state.editar_comida_planificador = comida['id']
                                    st.session_state.mostrar_form_comida_planificador = True
                                    st.rerun()

                            with col_delete:
                                if st.button("🗑️ Eliminar",
                                             key=f"del_{comida['id']}",
                                             use_container_width=True,
                                             help="Eliminar esta comida"):  # Tooltip añadido
                                    if delete_data(f"/meals/{comida['id']}"):
                                        st.success("Comida eliminada")
                                        clear_caches()
                                        st.rerun()

                # Actualizar totales nutricionales
                for key in total_nutrients:
                    total_nutrients[key] += comida["nutrients"][key]

            # Mostrar resumen nutricional del día con un contenedor con borde
            st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("""
                <h3 style='margin-top:0; margin-bottom:15px; color:#64B5F6; font-size:1.3em;'>
                    📊 Resumen nutricional del día
                </h3>
                """, unsafe_allow_html=True)

                # Métricas en línea con mejor estilo
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🔥 Calorías", f"{total_nutrients['kcal']:.0f} kcal")
                col2.metric("🥩 Proteínas", f"{total_nutrients['protein_g']:.1f} g")
                col3.metric("🍚 Carbos", f"{total_nutrients['carbs_g']:.1f} g")
                col4.metric("🧈 Grasas", f"{total_nutrients['fat_g']:.1f} g")
        else:
            # Estado vacío - sin comidas (mensaje mejorado)
            st.markdown("""
            <div style='background-color:rgba(100,181,246,0.1); padding:20px; border-radius:5px; text-align:center; margin:20px 0;'>
                <p style='margin:0; font-size:16px; color:#64B5F6;'>ℹ️ No hay comidas registradas para este día</p>
                <p style='margin:5px 0 0 0; font-size:14px; opacity:0.8;'>
                    Usa el botón "Crear comida" para añadir una comida a esta fecha
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ---- TAB: VISTA SEMANAL ----
    with tab_semana:
        # Título mejorado para la semana
        st.markdown(f"""
        <h3 style='margin-top:15px; margin-bottom:20px; color:#64B5F6; display:flex; align-items:center; gap:8px;'>
            📆 Semana: {lunes.strftime('%d/%m')} - {(lunes + timedelta(days=6)).strftime('%d/%m/%Y')}
        </h3>
        """, unsafe_allow_html=True)

        # Mostrar tarjeta para cada día de la semana
        for i in range(7):
            dia = lunes + timedelta(days=i)
            dia_iso = dia.isoformat()

            # Buscar comidas para este día
            comidas_dia = [c for c in comidas if c.get('meal_date') == dia_iso]

            # Crear tarjeta para el día con mejor estilo
            with st.container(border=True):
                # Añadir clase visual dependiendo si es día actual
                es_dia_actual = dia == fecha_actual
                estilo_fondo = "background-color:rgba(100,181,246,0.1);" if es_dia_actual else ""

                col1, col2 = st.columns([3, 1])

                # Cabecera del día mejorada
                with col1:
                    dia_nombre = dia.strftime("%A, %d/%m")

                    if es_dia_actual:
                        st.markdown(f"""
                        <div style='{estilo_fondo} padding:8px; border-radius:5px;'>
                            <p style='margin:0; font-weight:bold; font-size:1.1em; color:#64B5F6;'>
                                🔵 {dia_nombre}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='{estilo_fondo} padding:8px; border-radius:5px;'>
                            <p style='margin:0; font-weight:bold; font-size:1.1em;'>
                                {dia_nombre}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                # Botones mejorados en columna derecha
                with col2:
                    if st.button("👁️ Ver detalles",
                                 key=f"ver_{i}",
                                 use_container_width=True,
                                 help=f"Ver detalle del {dia.strftime('%d/%m/%Y')}"):  # Tooltip añadido
                        st.session_state.fecha_planificador = dia
                        st.rerun()

                    if st.button("✨ Crear comida",
                                 type="primary",
                                 use_container_width=True,
                                 key=f'crear-comida_{i}',
                                 help=f"Añadir comida para el {dia.strftime('%d/%m/%Y')}"):  # Tooltip añadido
                        st.session_state.fecha_planificador = dia  # Actualizar la fecha seleccionada
                        st.session_state.mostrar_form_comida_planificador = True
                        st.rerun()

                # Contenido del día mejorado
                if comidas_dia:
                    # Calcular totales
                    total_dia = {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

                    for comida in comidas_dia:
                        for key in total_dia:
                            total_dia[key] += comida["nutrients"][key]

                    # Mostrar resumen de comidas con mejor formato
                    st.markdown(f"""
                    <div style='margin-top:8px; display:flex; align-items:center; gap:15px;'>
                        <span style='font-weight:500;'>
                            <span style='color:#64B5F6;'>{len(comidas_dia)}</span> comidas
                        </span>
                        <span>•</span>
                        <span style='font-weight:500;'>
                            <span style='color:#FF9800;'>{total_dia['kcal']:.0f}</span> kcal
                        </span>
                        <span>•</span>
                        <span style='font-weight:500;'>
                            P: <span style='color:#E91E63;'>{total_dia['protein_g']:.0f}</span> g
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Mostrar recetas en tarjetas compactas
                    todas_recetas = []
                    for comida in comidas_dia:
                        for item in comida.get("items", []):
                            if item["component_type"] == "recipe":
                                todas_recetas.append(get_recipe_name(item["component_id"]))

                    if todas_recetas:
                        st.markdown(f"""
                        <div style='margin-top:5px; padding:8px; background-color:rgba(255,255,255,0.05); border-radius:4px;'>
                            <p style='margin:0; font-size:0.9em; color:#BBBBBB;'>
                                🍽️ {", ".join(todas_recetas[:5]) + ("..." if len(todas_recetas) > 5 else "")}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Mensaje mejorado para día sin comidas
                    st.markdown("""
                    <div style='padding:10px; text-align:center; color:#AAAAAA; font-size:0.9em;'>
                        No hay comidas registradas
                    </div>
                    """, unsafe_allow_html=True)


def formulario_comida(fecha_seleccionada, recetas: List[dict], alimentos: List[dict],
                  comida_existente: Optional[dict] = None) -> Optional[dict]:
    """
    Formulario para crear o editar una comida.
    Permite añadir/eliminar recetas y alimentos individuales.

    Args:
        fecha_seleccionada: Fecha seleccionada en el planificador
        recetas: Lista de recetas disponibles
        alimentos: Lista de alimentos disponibles
        comida_existente: Datos de comida existente si estamos editando

    Returns:
        dict con los datos de la comida o None si se cancela
    """
    from datetime import date  # Importación explícita para evitar confusiones

    # Título según modo (crear o editar) - Mejorado con estilos visuales
    if comida_existente:
        st.markdown(f"""
        <h2 style="color:#64B5F6; margin-bottom:20px; display:flex; align-items:center; gap:8px;">
            <span>✏️</span> <span>Editar comida del {comida_existente.get('meal_date', '')}</span>
        </h2>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <h2 style="color:#64B5F6; margin-bottom:20px; display:flex; align-items:center; gap:8px;">
            <span>➕</span> <span>Crear nueva comida</span>
        </h2>
        """, unsafe_allow_html=True)

    # Inicializar estado para almacenar temporalmente recetas y alimentos
    if 'comida_recetas_temp' not in st.session_state:
        if comida_existente:
            # Si editamos, extraer recetas de la comida existente
            st.session_state.comida_recetas_temp = []
            for item in comida_existente.get('items', []):
                if item['component_type'] == 'recipe':
                    receta = next((r for r in recetas if r['id'] == item['component_id']), None)
                    if receta:
                        st.session_state.comida_recetas_temp.append(receta['name'])
        else:
            st.session_state.comida_recetas_temp = []

    if 'comida_alimentos_temp' not in st.session_state:
        if comida_existente:
            # Si editamos, extraer alimentos de la comida existente
            st.session_state.comida_alimentos_temp = []
            for item in comida_existente.get('items', []):
                if item['component_type'] == 'food':
                    alimento = next((a for a in alimentos if a['id'] == item['component_id']), None)
                    if alimento:
                        st.session_state.comida_alimentos_temp.append({
                            "nombre": alimento['name'],
                            "cantidad": item['quantity']
                        })
        else:
            st.session_state.comida_alimentos_temp = []

    # SECCIÓN 1: FECHA Y DATOS BÁSICOS - Agrupada en container con borde
    with st.container(border=True):  # Contenedor con borde para agrupar elementos relacionados
        st.markdown("""
        <h5 style='margin-top:0; margin-bottom:10px; color:#64B5F6;'>
            📆 Información básica
        </h5>
        """, unsafe_allow_html=True)

        col_fecha, col_info = st.columns([1, 2])

        with col_fecha:
            # Usar la fecha seleccionada del planificador como valor por defecto
            fecha_comida = st.date_input(
                "Fecha de la comida",
                value=date.fromisoformat(comida_existente.get('meal_date')) if comida_existente else fecha_seleccionada,
                key="fecha_comida",
                help="Selecciona la fecha para esta comida"  # Tooltip informativo
            )

        with col_info:
            try:
                # Obtener comidas para esta fecha
                comidas_del_dia = []
                comidas_response = fetch_data("/meals")
                if comidas_response:
                    comidas_del_dia = [c for c in comidas_response if c.get('meal_date') == fecha_comida.isoformat()]

                    # Filtrar la comida que estamos editando
                    if comida_existente:
                        comidas_del_dia = [c for c in comidas_del_dia if c['id'] != comida_existente['id']]

                    if comidas_del_dia:
                        st.markdown(f"""
                        <p style='margin-bottom:8px; font-weight:500; color:#64B5F6;'>
                            <i>Comidas existentes para el {fecha_comida.strftime('%d/%m/%Y')}:</i>
                        </p>
                        """, unsafe_allow_html=True)

                        # Mostrar cada comida
                        for comida in comidas_del_dia:
                            with st.container(border=True):  # Contenedor con borde para cada comida
                                # Distribución mejorada de columnas
                                col1, col2, col3 = st.columns([5, 5, 1.6], gap='medium')

                                with col1:
                                    # Mostrar recetas
                                    recetas_items = [item for item in comida.get("items", []) if item.get("component_type") == "recipe"]
                                    if recetas_items:
                                        recetas_nombres = []
                                        for item in recetas_items:
                                            # Buscar directamente el nombre de la receta
                                            recipe_id = item['component_id']
                                            recipe_name = f"Receta #{recipe_id}"  # Valor predeterminado
                                            for r in recetas:
                                                if r['id'] == recipe_id:
                                                    recipe_name = r['name']
                                                    break
                                            recetas_nombres.append(f"🍽️ {recipe_name}")
                                        st.write(", ".join(recetas_nombres))

                                with col2:
                                    # Mostrar alimentos
                                    alimentos_items = [item for item in comida.get("items", []) if item.get("component_type") == "food"]
                                    if alimentos_items:
                                        alimentos_nombres = []
                                        for item in alimentos_items:
                                            # Buscar directamente el nombre del alimento
                                            food_id = item['component_id']
                                            food_name = f"Alimento #{food_id}"  # Valor predeterminado
                                            for a in alimentos:
                                                if a['id'] == food_id:
                                                    food_name = a['name']
                                                    break
                                            alimentos_nombres.append(f"🥗 {food_name} ({item['quantity']}g)")
                                        st.write(", ".join(alimentos_nombres))

                                with col3:
                                    # Botón de editar estilizado
                                    if st.button(f"✏️ Editar", use_container_width=True, key=f"edit_comida_{comida['id']}",
                                                type="secondary"):  # Tipo de botón definido para consistencia
                                        st.session_state.editar_comida_planificador = comida['id']
                                        st.session_state.mostrar_form_comida_planificador = True
                                        st.rerun()

                                # Valores nutricionales en chips visuales
                                st.markdown("<div style='display:flex; gap:12px; margin-top:6px;'>", unsafe_allow_html=True)
                                col1, col2, col3, col4 = st.columns(4)
                                col1.markdown(f"<div style='background-color:rgba(255,152,0,0.1); padding:4px 10px; border-radius:10px; text-align:center;'>🔥 {comida['nutrients']['kcal']:.0f} kcal</div>", unsafe_allow_html=True)
                                col2.markdown(f"<div style='background-color:rgba(233,30,99,0.1); padding:4px 10px; border-radius:10px; text-align:center;'>🥩 {comida['nutrients']['protein_g']:.1f}g</div>", unsafe_allow_html=True)
                                col3.markdown(f"<div style='background-color:rgba(3,169,244,0.1); padding:4px 10px; border-radius:10px; text-align:center;'>🍚 {comida['nutrients']['carbs_g']:.1f}g</div>", unsafe_allow_html=True)
                                col4.markdown(f"<div style='background-color:rgba(0,150,136,0.1); padding:4px 10px; border-radius:10px; text-align:center;'>🧈 {comida['nutrients']['fat_g']:.1f}g</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                    else:
                        st.info("Añade recetas y alimentos individuales a esta comida. Los valores nutricionales se calcularán automáticamente.")
                else:
                    st.info("Añade recetas y alimentos individuales a esta comida. Los valores nutricionales se calcularán automáticamente.")
            except Exception as e:
                st.error(f"Error al obtener comidas existentes: {str(e)}")
                st.info("Añade recetas y alimentos individuales a esta comida. Los valores nutricionales se calcularán automáticamente.")

        # NUEVA SECCIÓN: Resumen de comidas existentes para la fecha seleccionada
        try:
            # Intentar obtener las comidas para esta fecha
            comidas_del_dia = []
            comidas_response = fetch_data("/meals")
            if comidas_response:
                comidas_del_dia = [c for c in comidas_response if c.get('meal_date') == fecha_comida.isoformat()]

                # Filtrar la comida que estamos editando si es necesario
                if comida_existente:
                    comidas_del_dia = [c for c in comidas_del_dia if c['id'] != comida_existente['id']]

                # Si hay comidas, mostrar resumen con estilo mejorado
                if comidas_del_dia:
                    st.markdown(f"""
                    <div style='background-color:rgba(255,193,7,0.1); padding:10px 15px; border-radius:5px; 
                         margin-top:10px; display:flex; align-items:center;'>
                        <span style='font-size:18px; margin-right:10px'>⚠️</span> 
                        <span>Ya existen {len(comidas_del_dia)} comidas para el {fecha_comida.strftime('%d/%m/%Y')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al obtener comidas existentes: {str(e)}")

    # Espacio entre secciones
    st.markdown("<div style='margin:15px 0;'></div>", unsafe_allow_html=True)

    # REORGANIZACIÓN DE PANELES DE RECETAS Y ALIMENTOS - Mejorado con contenedor
    with st.container(border=True):  # Agrupación visual
        st.markdown("""
        <h5 style='margin-top:0; margin-bottom:15px; color:#64B5F6;'>
            ➕ Añadir componentes
        </h5>
        """, unsafe_allow_html=True)

        # Crear dos columnas para los selectores con distribución mejorada
        col_recetas, col_alimentos, col_cantidad = st.columns([2, 2, 1], gap='medium')

        # SELECTOR DE RECETAS - Columna izquierda con etiqueta mejorada
        with col_recetas:
            st.markdown("<label style='font-weight:500; color:#64B5F6;'>🍽️ Seleccionar receta</label>", unsafe_allow_html=True)
            # Lista de nombres de recetas para seleccionar
            nombres_recetas = [r['name'] for r in recetas if r['name'] not in st.session_state.comida_recetas_temp]
            receta_seleccionada = st.selectbox(
                "Seleccionar receta",
                options=[""] + nombres_recetas,
                key="receta_select",
                label_visibility="collapsed"  # Ocultar etiqueta duplicada
            )

        # SELECTOR DE ALIMENTOS - Columna derecha con etiqueta mejorada
        with col_alimentos:
            st.markdown("<label style='font-weight:500; color:#64B5F6;'>🥗 Seleccionar alimento</label>", unsafe_allow_html=True)
            # Filtrar alimentos ya añadidos
            alimentos_disponibles = [a['name'] for a in alimentos]
            nombre_alim_seleccionado = st.selectbox(
                "Seleccionar alimento",
                options=[""] + alimentos_disponibles,
                key="alim_select",
                label_visibility="collapsed"
            )

            # Obtener el objeto completo del alimento
            alim_completo = next((a for a in alimentos if a['name'] == nombre_alim_seleccionado), None)

            # Determinar el step según el valor de unit del alimento
            step_valor = 10.0  # Valor predeterminado (convertido a float)
            if alim_completo and alim_completo.get("unit") is not None:
                step_valor = float(alim_completo["unit"])

            # Inicializar el contador del botón si no existe
            if 'btn_medio_count' not in st.session_state:
                st.session_state.btn_medio_count = 0

            # Inicializar el valor de cantidad si no existe o si cambia el alimento
            if 'ultimo_alimento' not in st.session_state or st.session_state.ultimo_alimento != nombre_alim_seleccionado:
                st.session_state.cantidad_valor = float(step_valor) if step_valor > 1 else 100.0
                st.session_state.ultimo_alimento = nombre_alim_seleccionado

        with col_cantidad:
            txt = ""
            if alim_completo:
                cat = alim_completo.get("category", "")
                if cat == 'Aceites y grasas':
                    txt = "Cucharada/s"
                elif cat == 'Bebidas':
                    txt = "Vasos/s"
                elif cat in ['Frutas', 'Verduras y hortalizas']:
                    txt = "Pieza/s"

            st.markdown("<label style='font-weight:500; color:#64B5F6;'>Cantidad</label>", unsafe_allow_html=True)

            # Crear dos columnas para el input y el botón +1/2
            col_input, col_medio = st.columns([3, 1])

            with col_input:
                # Usar un contador en la clave para forzar recreación del widget
                cantidad_g = st.number_input(
                    "Cantidad (g)",
                    min_value=1.0,
                    max_value=1000.0,
                    value=st.session_state.cantidad_valor,
                    step=step_valor,
                    key=f"alim_cantidad_{st.session_state.btn_medio_count}",
                    help="Gramos de alimento a añadir",
                    label_visibility="collapsed"
                )
                # Actualizar el valor en session_state
                st.session_state.cantidad_valor = cantidad_g

            # Botón +1/2 unidad a la derecha
            with col_medio:
                boton_disabled = not (alim_completo and alim_completo.get("unit") is not None)
                if st.button("+1/2",
                           disabled=boton_disabled,
                           use_container_width=True,
                           key="btn_medio_unit"):
                    if not boton_disabled:
                        # Incrementar en la mitad de la unidad
                        medio_step = float(alim_completo["unit"]) / 2
                        # Actualizar el valor en session_state
                        st.session_state.cantidad_valor += medio_step
                        # Incrementar el contador para forzar recreación del widget
                        st.session_state.btn_medio_count += 1
                        st.rerun()

            if txt:
                st.markdown(f'{round(cantidad_g / step_valor, 1)} {txt}')

        # Botones con mejor alineación y márgenes
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        col_añadir_receta, col_añadir_alimento = st.columns([1, 1.52], gap='medium')

        with col_añadir_receta:
            if st.button("➕ Añadir receta",
                         disabled=not receta_seleccionada,
                         use_container_width=True,
                         type="primary" if receta_seleccionada else "secondary"):  # Destacar si hay selección
                if receta_seleccionada:
                    st.session_state.comida_recetas_temp.append(receta_seleccionada)
                    st.rerun()

        with col_añadir_alimento:
            if st.button("➕ Añadir alimento",
                         disabled=not nombre_alim_seleccionado,  # Corregido
                         use_container_width=True,
                         type="primary" if nombre_alim_seleccionado else "secondary"):  # Corregido
                if nombre_alim_seleccionado:  # Corregido
                    # Añadir el alimento a la lista temporal
                    st.session_state.comida_alimentos_temp.append({
                        "nombre": nombre_alim_seleccionado,
                        "cantidad": cantidad_g
                    })
                    st.rerun()  # Refrescar para mostrar el alimento añadido

    # Espacio entre secciones
    st.markdown("<div style='margin:15px 0;'></div>", unsafe_allow_html=True)

    # TABLA UNIFICADA DE ELEMENTOS AÑADIDOS
    with st.container(border=True):  # Contenedor con borde para elementos añadidos
        st.markdown("""
        <h5 style='margin-top:0; margin-bottom:15px; color:#64B5F6;'>
            📋 Elementos añadidos
        </h5>
        """, unsafe_allow_html=True)

        # Verificar si hay elementos añadidos
        hay_elementos = bool(st.session_state.comida_recetas_temp or st.session_state.comida_alimentos_temp)

        if hay_elementos:
            # Crear lista unificada de datos
            elementos_data = []

            # Añadir recetas a la tabla unificada
            for idx, nombre_receta in enumerate(st.session_state.comida_recetas_temp):
                receta_info = next((r for r in recetas if r['name'] == nombre_receta), None)
                if receta_info:
                    elementos_data.append({
                        "Tipo": "🍽️ Receta",
                        "Nombre": nombre_receta,
                        "Cantidad": "-",
                        "Kcal": round(receta_info.get('nutrients', {}).get('kcal', 0), 1),
                        "Proteínas (g)": round(receta_info.get('nutrients', {}).get('protein_g', 0), 1),
                        "Carbos (g)": round(receta_info.get('nutrients', {}).get('carbs_g', 0), 1),
                        "Grasas (g)": round(receta_info.get('nutrients', {}).get('fat_g', 0), 1),
                        "ID": f"R_{idx}"  # Prefijo R para recetas
                    })

            # Añadir alimentos a la tabla unificada
            for idx, alim in enumerate(st.session_state.comida_alimentos_temp):
                alim_info = next((a for a in alimentos if a['name'] == alim["nombre"]), None)
                if alim_info:
                    factor = alim["cantidad"] / 100
                    elementos_data.append({
                        "Tipo": "🥗 Alimento",
                        "Nombre": alim["nombre"],
                        "Cantidad": f"{alim['cantidad']} g",
                        "Kcal": round(alim_info.get('nutrients', {}).get('kcal', 0) * factor, 1),
                        "Proteínas (g)": round(alim_info.get('nutrients', {}).get('protein_g', 0) * factor, 1),
                        "Carbos (g)": round(alim_info.get('nutrients', {}).get('carbs_g', 0) * factor, 1),
                        "Grasas (g)": round(alim_info.get('nutrients', {}).get('fat_g', 0) * factor, 1),
                        "ID": f"A_{idx}"  # Prefijo A para alimentos
                    })

            # Mostrar tabla unificada con mejor formato
            col_tabla, col_botones = st.columns([6, 1])

            with col_tabla:
                if elementos_data:
                    df_elementos = pd.DataFrame(elementos_data)
                    # Excluir columna ID de la visualización
                    df_display = df_elementos.drop(columns=['ID'])
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True,
                        column_config={  # Configuración de columnas para mejor visualización
                            "Tipo": st.column_config.TextColumn("Tipo"),
                            "Nombre": st.column_config.TextColumn("Nombre"),
                            "Cantidad": st.column_config.TextColumn("Cantidad"),
                            "Kcal": st.column_config.NumberColumn("Kcal", format="%.1f"),
                            "Proteínas (g)": st.column_config.NumberColumn("Proteínas (g)", format="%.1f"),
                            "Carbos (g)": st.column_config.NumberColumn("Carbos (g)", format="%.1f"),
                            "Grasas (g)": st.column_config.NumberColumn("Grasas (g)", format="%.1f"),
                        }
                    )

            # Botones de eliminación con mejor estilo
            with col_botones:
                st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)  # Alineación con tabla
                for elemento in elementos_data:
                    id_elemento = elemento["ID"]
                    tipo, idx = id_elemento.split('_')
                    idx = int(idx)

                    # Botones con tooltip
                    tooltip = f"Eliminar {elemento['Nombre']}"
                    if st.button(f"🗑️", key=f"del_{id_elemento}", help=tooltip):
                        if tipo == "R":
                            st.session_state.comida_recetas_temp.pop(idx)
                        else:  # tipo == "A"
                            st.session_state.comida_alimentos_temp.pop(idx)
                        st.rerun()
        else:
            # Mensaje vacío mejorado
            st.markdown("""
            <div style="background-color:rgba(100,181,246,0.1); padding:15px; border-radius:5px; text-align:center;">
                <p style="margin:0; font-size:15px;">⚠️ Aún no has añadido recetas ni alimentos</p>
                <p style="margin:5px 0 0 0; font-size:13px; opacity:0.8;">
                    Selecciona recetas y/o alimentos utilizando los selectores de arriba
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Espacio entre secciones
    st.markdown("<div style='margin:15px 0;'></div>", unsafe_allow_html=True)

    # SECCIÓN 4: RESUMEN NUTRICIONAL con mejor visualización
    with st.container(border=True):
        st.markdown("""
        <h5 style='margin-top:0; margin-bottom:15px; color:#64B5F6;'>
            📊 Resumen nutricional
        </h5>
        """, unsafe_allow_html=True)

        # Inicializar total_nutrients fuera de la condición para que esté siempre disponible
        total_nutrients = {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

        # Calcular totales nutricionales solo si hay elementos
        if st.session_state.comida_recetas_temp or st.session_state.comida_alimentos_temp:
            # Sumar nutrientes de recetas
            for nombre_receta in st.session_state.comida_recetas_temp:
                receta_info = next((r for r in recetas if r['name'] == nombre_receta), None)
                if receta_info and 'nutrients' in receta_info:
                    for key in total_nutrients:
                        total_nutrients[key] += receta_info['nutrients'].get(key, 0)

            # Sumar nutrientes de alimentos
            for alim in st.session_state.comida_alimentos_temp:
                alim_info = next((a for a in alimentos if a['name'] == alim["nombre"]), None)
                if alim_info and 'nutrients' in alim_info:
                    factor = alim["cantidad"] / 100
                    for key in total_nutrients:
                        total_nutrients[key] += alim_info['nutrients'].get(key, 0) * factor

        # Mostrar resumen en fila con emojis y tarjetas mejoradas
        col_kcal, col_prot, col_carb, col_fat = st.columns(4)

        # Tarjetas estilizadas para los nutrientes
        with col_kcal:
            st.markdown(f"""
            <div style="background-color:rgba(255,152,0,0.1); padding:10px; border-radius:8px; text-align:center;">
                <div style="font-size:14px; opacity:0.8;">🔥 Calorías</div>
                <div style="font-size:20px; font-weight:bold;">{total_nutrients['kcal']:.0f} kcal</div>
            </div>
            """, unsafe_allow_html=True)

        with col_prot:
            st.markdown(f"""
            <div style="background-color:rgba(233,30,99,0.1); padding:10px; border-radius:8px; text-align:center;">
                <div style="font-size:14px; opacity:0.8;">🥩 Proteínas</div>
                <div style="font-size:20px; font-weight:bold;">{total_nutrients['protein_g']:.1f} g</div>
            </div>
            """, unsafe_allow_html=True)

        with col_carb:
            st.markdown(f"""
            <div style="background-color:rgba(3,169,244,0.1); padding:10px; border-radius:8px; text-align:center;">
                <div style="font-size:14px; opacity:0.8;">🍚 Carbohidratos</div>
                <div style="font-size:20px; font-weight:bold;">{total_nutrients['carbs_g']:.1f} g</div>
            </div>
            """, unsafe_allow_html=True)

        with col_fat:
            st.markdown(f"""
            <div style="background-color:rgba(0,150,136,0.1); padding:10px; border-radius:8px; text-align:center;">
                <div style="font-size:14px; opacity:0.8;">🧈 Grasas</div>
                <div style="font-size:20px; font-weight:bold;">{total_nutrients['fat_g']:.1f} g</div>
            </div>
            """, unsafe_allow_html=True)

        # Gráfico de distribución macronutrientes (solo si hay valores)
        hay_nutrientes = sum(total_nutrients.values()) > 0
        if hay_nutrientes:
            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
            col1, col2 = st.columns([2, 1])

            with col1:
                # Calcular calorías de cada macronutriente
                proteinas_kcal = total_nutrients['protein_g'] * 4
                carbos_kcal = total_nutrients['carbs_g'] * 4
                grasas_kcal = total_nutrients['fat_g'] * 9

                # Datos para el gráfico
                labels = ['Proteínas', 'Carbohidratos', 'Grasas']
                values = [proteinas_kcal, carbos_kcal, grasas_kcal]

                fig = px.pie(
                    names=labels,
                    values=values,
                    title='Distribución calórica',
                    color_discrete_sequence=['#2979FF', '#FF9800', '#00BCD4'],  # Colores mejorados
                    hole=0.4  # Gráfico tipo donut para mejor visualización
                )
                fig.update_layout(
                    margin=dict(t=30, b=0, l=0, r=0),
                    title_font_size=16,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Mostrar porcentajes con mejor formato
                total_kcal = sum(values)
                if total_kcal > 0:
                    st.markdown("<h6 style='margin-bottom:10px;'>Distribución de macros:</h6>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='margin-bottom:6px; display:flex; align-items:center;'>
                        <span style='color:#2979FF; font-size:20px;'>●</span>
                        <span style='margin-left:5px;'>Proteínas: {proteinas_kcal/total_kcal*100:.1f}%</span>
                    </div>
                    <div style='margin-bottom:6px; display:flex; align-items:center;'>
                        <span style='color:#FF9800; font-size:20px;'>●</span>
                        <span style='margin-left:5px;'>Carbohidratos: {carbos_kcal/total_kcal*100:.1f}%</span>
                    </div>
                    <div style='margin-bottom:6px; display:flex; align-items:center;'>
                        <span style='color:#00BCD4; font-size:20px;'>●</span>
                        <span style='margin-left:5px;'>Grasas: {grasas_kcal/total_kcal*100:.1f}%</span>
                    </div>
                    """, unsafe_allow_html=True)

    # SECCIÓN 5: BOTONES DE ACCIÓN con mejor estilo
    st.markdown("<div style='margin:20px 0 5px 0;'></div>", unsafe_allow_html=True)

    # Contenedor para botones con fondo ligeramente diferente
    with st.container():
        st.markdown("""
        <div style="background-color:rgba(25,25,25,0.2); height:1px; margin-bottom:15px;"></div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("❌ Cancelar",
                         use_container_width=True,
                         type="secondary"):  # Tipo secundario para menor énfasis
                # Limpiar estado temporal
                if 'comida_recetas_temp' in st.session_state:
                    del st.session_state.comida_recetas_temp
                if 'comida_alimentos_temp' in st.session_state:
                    del st.session_state.comida_alimentos_temp

                # Desactivar formulario directamente sin rerun
                st.session_state.mostrar_form_comida_planificador = False
                st.session_state.editar_comida_planificador = None
                st.rerun()
                return None

        with col2:
            # El botón de guardar siempre visible pero deshabilitado si no hay elementos
            hay_elementos = bool(st.session_state.comida_recetas_temp or st.session_state.comida_alimentos_temp)
            if st.button("💾 Guardar comida",
                         type="primary",
                         use_container_width=True,
                         disabled=not hay_elementos):
                # Esta parte solo se ejecuta cuando el botón está habilitado y se hace clic
                # Estructura de datos para enviar a la API
                comida_data = {
                    "meal_date": fecha_comida.isoformat(),
                    "recipes": st.session_state.comida_recetas_temp,
                    "foods": [
                        {item["nombre"]: item["cantidad"]}
                        for item in st.session_state.comida_alimentos_temp
                    ]
                }

                # Limpiar estado temporal
                if 'comida_recetas_temp' in st.session_state:
                    del st.session_state.comida_recetas_temp
                if 'comida_alimentos_temp' in st.session_state:
                    del st.session_state.comida_alimentos_temp

                return comida_data

    return None

