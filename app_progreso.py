import pandas as pd
import streamlit as st
import matplotlib
import os

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Título
st.title("Seguimiento y evolución del plan de entrenamiento")

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

      

    else:
        st.error("❌ No se encontró un archivo para ese ID. Verificá el código ingresado o consultá con tu entrenador.")
