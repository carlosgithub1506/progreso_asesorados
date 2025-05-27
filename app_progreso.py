import pandas as pd
import streamlit as st
import matplotlib
import os
from datetime import datetime
import pyexcel_ods3 as ods

matplotlib.use('Agg')
import matplotlib.pyplot as plt

st.markdown("<h1 style='color: #fc4817;'>FitTrapp</h1>", unsafe_allow_html=True)

st.subheader("Seguimiento y evolución del plan de entrenamiento")

# Ingreso del ID
id_usuario = st.text_input("🆔 Ingresá tu ID personal para ver tu rutina y evolución")

# Ruta base
base_path = "data"

if id_usuario:
    archivo_path = os.path.join(base_path, f"{id_usuario}.ods")

    if os.path.exists(archivo_path):
        st.success("✅ Archivo encontrado, cargando datos...")

        # === DATOS PERSONALES ===
        try:
            df_datos = pd.read_excel(archivo_path, engine="odf", sheet_name="Datos")
            nombre = df_datos.at[0, "Nombre"] if "Nombre" in df_datos.columns else ""
            apellido = df_datos.at[0, "Apellido"] if "Apellido" in df_datos.columns else ""
            nombre_completo = f"{nombre} {apellido}".strip()
            st.header(f" Bienvenido (a)  {nombre_completo}")
        except Exception as e:
            st.info("ℹ️ No se pudo cargar el nombre del asesorado.")
            st.text(str(e))

          # === NUTRICIÓN ===
        try:
            df_nutricion = pd.read_excel(archivo_path, engine="odf", sheet_name="Nutricion")
            df_nutricion_limpio = df_nutricion.dropna(how="all")

            st.subheader("🥗 Plan Nutricional")
            st.dataframe(df_nutricion_limpio)

            df_nutricion_limpio["Fecha"] = pd.to_datetime(df_nutricion_limpio["Fecha"], errors="coerce")
            df_nutricion_limpio = df_nutricion_limpio.dropna(subset=["Fecha"])
            df_nutricion_limpio.set_index("Fecha", inplace=True)

            columnas_nutricion = ["TMB (kcal)", "Proteínas (g)", "Carbohidratos (g)", "Grasas (g)"]

            with st.expander("📈 Evolución de TMB, Proteínas, Carbohidratos y Grasas"):
                fig, ax = plt.subplots(figsize=(10, 5))
                for col in columnas_nutricion:
                    if col in df_nutricion_limpio.columns:
                        ax.plot(df_nutricion_limpio.index, df_nutricion_limpio[col], marker='o', label=col)

                ax.set_title("Evolución Nutricional por Fecha")
                ax.set_xlabel("Fecha")
                ax.set_ylabel("Cantidad")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)

        except Exception as e:
            st.warning("⚠️ No se pudo cargar la hoja de nutrición.")
            st.text(str(e))

        # === MEDIDAS ===
        try:
            df_medidas = pd.read_excel(archivo_path, engine="odf", sheet_name="Medidas")
            df_medidas["Fecha"] = pd.to_datetime(df_medidas["Fecha"], errors="coerce")
            df_medidas = df_medidas.dropna(subset=["Fecha"])
            df_medidas.set_index("Fecha", inplace=True)

            st.subheader("📋 Tabla de Medidas")
            st.dataframe(df_medidas)

            columnas = ["Peso (kg)", "Pecho (cm)", "Cintura (cm)", "Gluteos (cm)", "Brazo (cm)", "Pierna (cm)"]

            for col in columnas:
                if col in df_medidas.columns:
                    with st.expander(f"📈 Evolución de {col}"):
                        fig, ax = plt.subplots(figsize=(8, 4))
                        ax.plot(df_medidas.index, df_medidas[col], marker='o', label=col)
                        ax.set_xlabel("Fecha")
                        ax.set_ylabel(col)
                        ax.set_title(f"Evolución de {col}")
                        ax.grid(True)
                        ax.legend()
                        st.pyplot(fig)

            with st.expander("📊 Evolución de Todas las Medidas"):
                fig, ax = plt.subplots(figsize=(10, 6))
                for col in columnas:
                    if col in df_medidas.columns:
                        ax.plot(df_medidas.index, df_medidas[col], marker='o', label=col)
                ax.set_title("Evolución de Medidas Corporales")
                ax.set_xlabel("Fecha")
                ax.set_ylabel("Valor")
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)

        except Exception as e:
            st.warning("⚠️ No se pudo cargar la hoja de medidas.")
            st.text(str(e))

        # === RUTINA COMPLETA ===
        try:
            df_rutina = pd.read_excel(archivo_path, engine="odf", sheet_name="Rutina")
            df_rutina_limpia = df_rutina.dropna(subset=["Ejercicio"])

            st.subheader("🏋️ Rutina de Ejercicios Completa")
            st.dataframe(df_rutina_limpia)

            # === FILTRO DE RUTINA ===
            st.subheader("Visualización Filtrada por Día")

            if not df_rutina_limpia.empty:
                dias = df_rutina_limpia["Día"].dropna().unique()
                dia_seleccionado = st.selectbox("🗖 Seleccioná un día de entrenamiento", sorted(dias)) if len(dias) > 0 else None

                if dia_seleccionado:
                    ejercicios_dia = df_rutina_limpia[df_rutina_limpia["Día"] == dia_seleccionado]

                    st.subheader("Rutina de ejercicios del día")
                    st.dataframe(ejercicios_dia[["Ejercicio", "Grupo Muscular", "Series", "Repeticiones", "Peso (kg)", "Descanso (min)"]].reset_index(drop=True))

                    with st.expander("📈 Resumen gráfico del volumen de series del día"):
                        valores_agrupados = ejercicios_dia.groupby("Grupo Muscular")["Series"].sum()
                        if not valores_agrupados.empty:
                            fig, ax = plt.subplots(figsize=(8, 4))
                            valores_agrupados.plot(kind="bar", ax=ax, color="skyblue")
                            ax.set_ylabel("Total de Series")
                            ax.set_xlabel("Grupo Muscular")
                            ax.set_title(f"Total de Series por Grupo Muscular - {dia_seleccionado}")
                            ax.grid(True)
                            st.pyplot(fig)

        except Exception as e:
            st.warning("⚠️ No se pudo cargar la hoja de rutina.")
            st.text(str(e))

  

# === REGISTRO DE PROGRESO DE EJERCICIO ===


if id_usuario and 'df_rutina_limpia' in locals() and not df_rutina_limpia.empty:
    st.markdown("#### 📌 Registro de Progreso Personalizado")
    dias = df_rutina_limpia["Día"].dropna().unique()
    dia_seleccionado_prog = st.selectbox("🗓 Seleccioná el día de rutina para registrar tu progreso", sorted(dias), key="dia_prog")

    if dia_seleccionado_prog:
        ejercicios_dia_prog = df_rutina_limpia[df_rutina_limpia["Día"] == dia_seleccionado_prog]
        ejercicios = ejercicios_dia_prog["Ejercicio"].dropna().unique()
        ejercicio_seleccionado = st.selectbox("🏋️ Elegí un ejercicio para registrar", sorted(ejercicios))

        if ejercicio_seleccionado:
            num_series = st.number_input("📌 Ingresá la cantidad de series realizadas", min_value=1, max_value=10, value=3)
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            st.markdown(f"#### ✍️ Ingresá los datos de {ejercicio_seleccionado} - {fecha_actual}")

            repeticiones = []
            peso = []
            descanso = []

            for i in range(int(num_series)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    reps = st.number_input(f"Repeticiones Serie {i+1}", min_value=0, key=f"reps_{i}")
                with col2:
                    kg = st.number_input(f"Peso (kg) Serie {i+1}", min_value=0.0, key=f"peso_{i}")
                with col3:
                    rest = st.number_input(f"Descanso (seg) Serie {i+1}", min_value=0.0, key=f"desc_{i}")

                repeticiones.append(reps)
                peso.append(kg)
                descanso.append(rest)

            if st.button("💾 Guardar Progreso"):
                progreso_path = os.path.join(base_path, f"{id_usuario}_{ejercicio_seleccionado}.ods")

                fila_fecha = ["Fecha", fecha_actual]
                filas_nuevas = [["Serie", "Repeticiones", "Peso (kg)", "Descanso (minutos)"]]
                for i in range(int(num_series)):
                    filas_nuevas.append([i + 1, repeticiones[i], peso[i], descanso[i]])

                if os.path.exists(progreso_path):
                    try:
                        datos_existentes = ods.get_data(progreso_path)
                        hoja = list(datos_existentes.keys())[0]
                        datos_existentes[hoja].append([""])
                        datos_existentes[hoja].append(fila_fecha)
                        datos_existentes[hoja].extend(filas_nuevas)
                        ods.save_data(progreso_path, datos_existentes)
                    except Exception as e:
                        st.error(f"Error al actualizar el archivo: {e}")
                else:
                    hoja = "Progreso"
                    datos_nuevos = {hoja: [fila_fecha] + filas_nuevas}
                    try:
                        ods.save_data(progreso_path, datos_nuevos)
                    except Exception as e:
                        st.error(f"Error al crear el archivo: {e}")

                st.success("✅ Progreso guardado correctamente.")

            # === GRAFICAR PROGRESO HISTÓRICO ===
            st.markdown("#### 📊 Evolución del Ejercicio en el Tiempo")

            try:
                progreso_path = os.path.join(base_path, f"{id_usuario}_{ejercicio_seleccionado}.ods")
                if os.path.exists(progreso_path):
                    datos_raw = ods.get_data(progreso_path)
                    hoja = list(datos_raw.keys())[0]
                    datos = datos_raw[hoja]

                    registros = []
                    fecha_actual = None
                    for fila in datos:
                        if not fila:
                            continue
                        if fila[0] == "Fecha":
                            fecha_actual = fila[1]
                        elif isinstance(fila, list) and len(fila) == 4 and fila[0] != "Serie":
                            try:
                                registros.append({
                                    "Fecha": fecha_actual,
                                    "Serie": int(fila[0]),
                                    "Repeticiones": int(fila[1]),
                                    "Peso": float(fila[2]),
                                    "Descanso": float(fila[3])
                                })
                            except:
                                pass

                    df_progreso = pd.DataFrame(registros)
                    df_progreso["Fecha"] = pd.to_datetime(df_progreso["Fecha"])

                    with st.expander("##### 📈 Evolución de Peso Usado por Fecha"):
                        fig, ax = plt.subplots(figsize=(8, 4))
                        df_peso = df_progreso.groupby("Fecha")["Peso"].mean()
                        ax.plot(df_peso.index, df_peso.values, marker='o', label="Peso Promedio")
                        ax.set_title("Peso Promedio por Fecha")
                        ax.set_xlabel("Fecha")
                        ax.set_ylabel("Peso (kg)")
                        ax.grid(True)
                        ax.legend()
                        st.pyplot(fig)

                    with st.expander("📈 Evolución de Repeticiones Totales por Fecha"):
                        fig, ax = plt.subplots(figsize=(8, 4))
                        df_reps = df_progreso.groupby("Fecha")["Repeticiones"].sum()
                        ax.plot(df_reps.index, df_reps.values, marker='o', color="orange", label="Reps Totales")
                        ax.set_title("Repeticiones Totales por Fecha")
                        ax.set_xlabel("Fecha")
                        ax.set_ylabel("Repeticiones")
                        ax.grid(True)
                        ax.legend()
                        st.pyplot(fig)

            except Exception as e:
                st.warning("⚠️ No se pudo leer o graficar los datos de progreso.")
                st.text(str(e))


      

    else:
        st.error("❌ No se encontró un archivo para ese ID. Verificá el código ingresado o consultá con tu entrenador!!!.")
