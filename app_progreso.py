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
                    st.subheader(f"📈 Evolución de {col}")
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(df_medidas.index, df_medidas[col], marker='o', label=col)
                    ax.set_xlabel("Fecha")
                    ax.set_ylabel(col)
                    ax.set_title(f"Evolución de {col}")
                    ax.grid(True)
                    ax.legend()
                    st.pyplot(fig)

            st.subheader("📊 Evolución de Todas las Medidas")
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

            st.subheader("🏋️ Tabla completa de la Rutina de Ejercicios")
            st.dataframe(df_rutina_limpia)

            # === FILTRO DE RUTINA ===
            st.subheader("🎯 Visualización Filtrada por Día")

            if not df_rutina_limpia.empty:
                dias = df_rutina_limpia["Día"].dropna().unique()
                dia_seleccionado = st.selectbox("📆 Seleccioná un día de entrenamiento", sorted(dias)) if len(dias) > 0 else None

                if dia_seleccionado:
                    ejercicios_dia = df_rutina_limpia[df_rutina_limpia["Día"] == dia_seleccionado]

                    st.markdown(f"### 📌 Ejercicios para el día **{dia_seleccionado}**")

                    st.subheader("📋 Tabla de ejercicios del día")
                    st.dataframe(ejercicios_dia[["Ejercicio", "Grupo Muscular", "Series", "Repeticiones", "Peso (kg)", "Descanso (min)"]].reset_index(drop=True))

                    # Mostrar gráfico general del día
                    st.subheader("📈 Resumen gráfico del día")
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

