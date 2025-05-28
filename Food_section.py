import requests
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from typing import List, Optional
from frontend_utils import fetch_data, post_data, update_data, delete_data, clear_caches

# Sección: Alimentos
def seccion_alimentos():
            # Estilizar el título principal con formato personalizado
            st.markdown("""
            <h1 style='text-align: center; color: #4CAF50; margin-bottom: 20px;'>
                🍽️ Gestión de Alimentos
            </h1>
            """, unsafe_allow_html=True)

            # Línea separadora estilizada
            st.markdown("<hr style='height: 2px; background-color: #4CAF50; border: none; margin: 10px 0 30px 0;'>", unsafe_allow_html=True)

            # Inicializar variables de estado si no existen
            if 'alimento_seleccionado' not in st.session_state:
                st.session_state.alimento_seleccionado = None
            if 'mostrar_form_editar_alimento' not in st.session_state:
                st.session_state.mostrar_form_editar_alimento = False
            if 'confirmar_eliminar_alimento' not in st.session_state:
                st.session_state.confirmar_eliminar_alimento = False
            if 'mostrar_form_alimento' not in st.session_state:
                st.session_state.mostrar_form_alimento = False
            if 'filtro_alimentos' not in st.session_state:
                st.session_state.filtro_alimentos = ""

            # Cargar alimentos desde la API
            alimentos = fetch_data("/foods")

            # Container principal con dos columnas
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Panel de alimentos registrados con borde y estilo
                    with st.container(border=True):
                        st.markdown("""
                        <h3 style='color: #4CAF50; margin-bottom: 15px;'>
                            📋 Alimentos registrados
                        </h3>
                        """, unsafe_allow_html=True)

                        if alimentos:
                            # Añadir filtro de búsqueda
                            st.session_state.filtro_alimentos = st.text_input(
                                "🔍 Buscar alimento",
                                value=st.session_state.filtro_alimentos,
                                placeholder="Escribe para filtrar..."
                            )

                            # Filtrar alimentos según el texto de búsqueda
                            alimentos_filtrados = alimentos
                            if st.session_state.filtro_alimentos:
                                alimentos_filtrados = [a for a in alimentos if st.session_state.filtro_alimentos.lower() in a['name'].lower()]

                            # Dataframe para mostrar alimentos
                            alimentos_df = pd.DataFrame([{
                                'Nombre': a['name'],
                                'Calorías': a['nutrients']['kcal'],
                                'Proteínas': a['nutrients']['protein_g'],
                                'Carbohidratos': a['nutrients']['carbs_g'],
                                'Grasas': a['nutrients']['fat_g'],
                                'Unidad': a.get('unit', 'N/A'),
                                'Mercado': a.get('market', 'N/A')
                            } for a in alimentos_filtrados])

                            # Ajustar altura dinámicamente con un mínimo
                            altura = max(300, min(100 + len(alimentos_filtrados) * 35, 600))
                            st.dataframe(
                                alimentos_df,
                                use_container_width=True,
                                height=altura,
                                hide_index=True,
                                column_config={
                                    "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                                    "Calorías": st.column_config.NumberColumn("🔥 Calorías", format="%.1f",
                                                                              width="small"),
                                    "Proteínas": st.column_config.NumberColumn("🥩 Proteínas (g)", format="%.1f",
                                                                               width="small"),
                                    "Carbohidratos": st.column_config.NumberColumn("🍚 Carbos (g)", format="%.1f",
                                                                                   width="small"),
                                    "Grasas": st.column_config.NumberColumn("🧈 Grasas (g)", format="%.1f",
                                                                            width="small"),
                                    "Unidad": st.column_config.TextColumn("⚖️ Unidad (g)", width="small"),
                                    "Mercado": st.column_config.TextColumn("🏪 Mercado", width="small"),
                                }
                            )

                            # Estadísticas resumen
                            with st.expander("📊 Estadísticas rápidas", expanded=False):
                                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                                with col_stats1:
                                    st.metric("Total alimentos", len(alimentos_filtrados))
                                with col_stats2:
                                    promedio_calorias = sum(a['nutrients']['kcal'] for a in alimentos_filtrados) / len(alimentos_filtrados)
                                    st.metric("Promedio calorías", f"{promedio_calorias:.1f}")
                                with col_stats3:
                                    max_proteina = max(a['nutrients']['protein_g'] for a in alimentos_filtrados)
                                    st.metric("Mayor proteína", f"{max_proteina:.1f} g")
                                with col_stats4:
                                    mercados = set(a.get('market') for a in alimentos_filtrados if a.get('market'))
                                    st.metric("Mercados", len(mercados))
                        else:
                            st.info("📝 No hay alimentos registrados. ¡Comienza agregando uno nuevo!")

                with col2:
                    # Panel de acciones con borde y estilo
                    with st.container(border=True):
                        st.markdown("""
                        <h3 style='color: #4CAF50; margin-bottom: 15px;'>
                            ⚙️ Acciones
                        </h3>
                        """, unsafe_allow_html=True)

                        # Botón de agregar alimento destacado
                        st.button(
                            "➕ Agregar nuevo alimento",
                            type="primary",
                            on_click=lambda: setattr(st.session_state, 'mostrar_form_alimento', True),
                            use_container_width=True
                        )

                        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

                        # Selector de alimento para editar/eliminar con estilo mejorado
                        if alimentos:
                            st.markdown("#### 🔍 Selecciona un alimento:")
                            opciones_alimentos = [(a["id"], a["name"]) for a in alimentos]
                            alimento_id = st.selectbox(
                                "Alimento",
                                options=[id for id, _ in opciones_alimentos],
                                format_func=lambda x: next((name for id, name in opciones_alimentos if id == x), ""),
                                key="selector_alimentos",
                                label_visibility="collapsed"
                            )

                            # Obtener el alimento seleccionado completo
                            if alimento_id:
                                alimento_seleccionado = next((a for a in alimentos if a["id"] == alimento_id), None)
                                st.session_state.alimento_seleccionado = alimento_seleccionado

                                # Mostrar información nutricional del alimento seleccionado
                                if alimento_seleccionado:
                                    with st.container(border=True):
                                        st.markdown(f"**{alimento_seleccionado['name']}**")
                                        col_info1, col_info2 = st.columns(2)
                                        with col_info1:
                                            st.caption(f"🔥 {alimento_seleccionado['nutrients']['kcal']:.1f} kcal")
                                            st.caption(f"🥩 {alimento_seleccionado['nutrients']['protein_g']:.1f} g")
                                        with col_info2:
                                            st.caption(f"🍚 {alimento_seleccionado['nutrients']['carbs_g']:.1f} g")
                                            st.caption(f"🧈 {alimento_seleccionado['nutrients']['fat_g']:.1f} g")

                            # Botones para editar y eliminar
                            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                            col1_btn, col2_btn = st.columns(2)
                            with col1_btn:
                                st.button(
                                    "✏️ Editar",
                                    type="secondary",
                                    on_click=lambda: setattr(st.session_state, 'mostrar_form_editar_alimento', True),
                                    disabled=not alimento_id,
                                    use_container_width=True
                                )

                            with col2_btn:
                                st.button(
                                    "🗑️ Eliminar",
                                    type="secondary",
                                    on_click=lambda: setattr(st.session_state, 'confirmar_eliminar_alimento', True),
                                    disabled=not alimento_id,
                                    use_container_width=True
                                )

            # Formulario para agregar alimento en un expander con estilo mejorado
            if st.session_state.mostrar_form_alimento:
                with st.container(border=True):
                    st.markdown("""
                    <h3 style='color: #4CAF50; margin-bottom: 15px;'>
                        ➕ Nuevo Alimento
                    </h3>
                    """, unsafe_allow_html=True)

                    with st.form("form_nuevo_alimento"):
                        # Campos básicos del alimento
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            nombre = st.text_input("Nombre del alimento", placeholder="Ej: Pollo, arroz, etc.")
                        with col2:
                            unidad = st.number_input("Peso por unidad (g)",
                                                    min_value=0.0,
                                                    value=0.0,
                                                    help="Peso aproximado de una unidad estándar en gramos (opcional)")
                        with col3:
                            mercado = st.text_input("Mercado", placeholder="Ej: Mercadona")

                        # Contenedor con borde para nutrientes
                        st.markdown("#### 📊 Información Nutricional (por 100g)")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            calorias = st.number_input("🔥 Calorías",
                                                      min_value=0.0,
                                                      format="%.1f",
                                                      help="Calorías por 100g del alimento")
                        with col2:
                            proteinas = st.number_input("🥩 Proteínas (g)",
                                                       min_value=0.0,
                                                       format="%.1f",
                                                       help="Gramos de proteína por 100g")
                        with col3:
                            carbohidratos = st.number_input("🍚 Carbohidratos (g)",
                                                           min_value=0.0,
                                                           format="%.1f",
                                                           help="Gramos de carbohidratos por 100g")
                        with col4:
                            grasas = st.number_input("🧈 Grasas (g)",
                                                    min_value=0.0,
                                                    format="%.1f",
                                                    help="Gramos de grasa por 100g")

                        # Botones del formulario
                        col_submit, col_cancel = st.columns([1, 1])
                        with col_submit:
                            submitted = st.form_submit_button("💾 Guardar alimento",
                                                             type="primary",
                                                             use_container_width=True)

                        with col_cancel:
                            canceled = st.form_submit_button("❌ Cancelar",
                                                           type="secondary",
                                                           use_container_width=True)

                        # Procesar el formulario
                        if submitted:
                            if nombre and calorias >= 0:
                                # Crear objeto de alimento para la API
                                alimento_data = {
                                    "name": nombre,
                                    "nutrients": {
                                        "kcal": calorias,
                                        "protein_g": proteinas,
                                        "fat_g": grasas,
                                        "carbs_g": carbohidratos,
                                    },
                                    "unit": int(unidad) if unidad > 0 else None,
                                    "market": mercado if mercado else None
                                }

                                # Enviar a la API
                                resultado = post_data("/foods", alimento_data)
                                if resultado:
                                    # Usar toast para notificación menos intrusiva
                                    st.toast(f"✅ Alimento '{nombre}' creado correctamente", icon="✅")
                                    st.session_state.mostrar_form_alimento = False
                                    clear_caches()  # Limpiar caché para actualizar la lista
                                    st.rerun()
                            else:
                                st.error("⚠️ El nombre y las calorías son obligatorios")

                        if canceled:
                            st.session_state.mostrar_form_alimento = False
                            st.rerun()

            # Formulario para editar alimento con estilo mejorado
            if st.session_state.mostrar_form_editar_alimento and st.session_state.alimento_seleccionado:
                alimento = st.session_state.alimento_seleccionado

                with st.container(border=True):
                    st.markdown(f"""
                    <h3 style='color: #4CAF50; margin-bottom: 15px;'>
                        ✏️ Editar: {alimento['name']}
                    </h3>
                    """, unsafe_allow_html=True)

                    with st.form("form_editar_alimento"):
                        # Campos básicos del alimento
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            nombre = st.text_input("Nombre del alimento", value=alimento['name'])
                        with col2:
                            unidad_valor = float(alimento['unit']) if alimento.get('unit') is not None else 0.0
                            unidad = st.number_input("Peso por unidad (g)",
                                                   min_value=0.0,
                                                   value=unidad_valor,
                                                   help="Peso aproximado de una unidad estándar en gramos (opcional)")
                        with col3:
                            mercado = st.text_input("Mercado", value=alimento.get('market', ""), placeholder="Ej: Mercadona")

                        # Contenedor con información nutricional
                        st.markdown("#### 📊 Información Nutricional (por 100g)")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            calorias = st.number_input("🔥 Calorías",
                                                      min_value=0.0,
                                                      value=alimento['nutrients']['kcal'],
                                                      format="%.1f")
                        with col2:
                            proteinas = st.number_input("🥩 Proteínas (g)",
                                                       min_value=0.0,
                                                       value=alimento['nutrients']['protein_g'],
                                                       format="%.1f")
                        with col3:
                            carbohidratos = st.number_input("🍚 Carbohidratos (g)",
                                                           min_value=0.0,
                                                           value=alimento['nutrients']['carbs_g'],
                                                           format="%.1f")
                        with col4:
                            grasas = st.number_input("🧈 Grasas (g)",
                                                    min_value=0.0,
                                                    value=alimento['nutrients']['fat_g'],
                                                    format="%.1f")

                        # Botones del formulario
                        col_submit, col_cancel = st.columns([1, 1])

                        with col_submit:
                            submitted = st.form_submit_button("💾 Actualizar",
                                                            type="primary",
                                                            use_container_width=True)

                        with col_cancel:
                            canceled = st.form_submit_button("❌ Cancelar",
                                                           type="secondary",
                                                           use_container_width=True)

                        # Procesar el formulario
                        if submitted:
                            if nombre:
                                # Crear objeto de alimento para la API
                                alimento_data = {
                                    "name": nombre,
                                    "nutrients": {
                                        "kcal": calorias,
                                        "protein_g": proteinas,
                                        "fat_g": grasas,
                                        "carbs_g": carbohidratos,
                                    },
                                    "unit": unidad if unidad > 0 else None,
                                    "market": mercado if mercado else None
                                }

                                # Enviar a la API
                                resultado = update_data(f"/foods/{alimento['id']}", alimento_data)
                                if resultado:
                                    # Toast para notificación menos intrusiva
                                    st.toast(f"✅ Alimento '{nombre}' actualizado correctamente", icon="✅")
                                    st.session_state.mostrar_form_editar_alimento = False
                                    st.session_state.alimento_seleccionado = None
                                    clear_caches()  # Limpiar caché para actualizar la lista
                                    st.rerun()
                            else:
                                st.error("⚠️ El nombre es obligatorio")

                        if canceled:
                            st.session_state.mostrar_form_editar_alimento = False
                            st.session_state.alimento_seleccionado = None
                            st.rerun()

            # Confirmación de eliminación de alimento con estilo mejorado
            if st.session_state.confirmar_eliminar_alimento and st.session_state.alimento_seleccionado:
                alimento = st.session_state.alimento_seleccionado

                with st.container(border=True):
                    st.markdown(f"""
                    <h3 style='color: #FF5252; margin-bottom: 15px;'>
                        ⚠️ Confirmar eliminación
                    </h3>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style='background-color: rgba(255, 82, 82, 0.1); padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                        <p>¿Estás seguro de que deseas eliminar el alimento <b>"{alimento['name']}"</b>?</p>
                        <p>Esta acción no se puede deshacer.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("⚠️ Sí, eliminar",
                                   type="primary",
                                   use_container_width=True):
                            resultado = delete_data(f"/foods/{alimento['id']}")
                            if resultado:
                                st.toast(f"✅ Alimento '{alimento['name']}' eliminado correctamente", icon="✅")
                                st.session_state.confirmar_eliminar_alimento = False
                                st.session_state.alimento_seleccionado = None
                                clear_caches()  # Limpiar caché para actualizar la lista
                                st.rerun()

                    with col2:
                        if st.button("❌ Cancelar",
                                   type="secondary",
                                   use_container_width=True):
                            st.session_state.confirmar_eliminar_alimento = False
                            st.session_state.alimento_seleccionado = None
                            st.rerun()




