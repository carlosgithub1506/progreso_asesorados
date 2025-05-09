
import pandas as pd
import streamlit as st
import matplotlib
import os

matplotlib.use('Agg')  # Usar un backend sin interfaz gráfica
import matplotlib.pyplot as plt

# Título de la aplicación
st.title("Seguimiento y evolución del plan de entrenamiento")

# Ingreso del ID
id_usuario = st.text_input("Ingresá tu ID personal para ver tu rutina y evolución")

# Ruta base
base_path = "data"

# Verificar si se ingresó un ID
if id_usuario:
    archivo_path = os.path.join(base_path, f"{id_usuario}.ods")

    if os.path.exists(archivo_path):
        st.success("✅ Archivo encontrado, cargando datos...")

        # Leer el archivo
        df = pd.read_excel(archivo_path, engine="odf", sheet_name="Medidas")

        # Procesar los datos
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.dropna(subset=["Fecha"])
        df.set_index("Fecha", inplace=True)

        # Mostrar tabla de medidas
        st.subheader("📋 Tabla de Medidas")
        st.dataframe(df)

        # Graficar medidas individuales
        columnas = ["Peso (kg)", "Pecho (cm)", "Cintura (cm)", "Gluteos (cm)", "Brazo (cm)", "Pierna (cm)"]
        for col in columnas:
            if col in df.columns:
                st.subheader(f"Evolución de {col}")
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(df.index, df[col], marker='o', label=col)
                ax.set_title(f"Evolución de {col}")
                ax.set_xlabel("Fecha")
                ax.set_ylabel(col)
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)

        # Gráfico combinado
        st.subheader("📈 Evolución de Todas las Medidas")
        fig, ax = plt.subplots(figsize=(10, 6))
        for col in columnas:
            if col in df.columns:
                ax.plot(df.index, df[col], marker='o', label=col)
        ax.set_title("Evolución de Medidas Corporales")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Valor")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # --- Tabla completa de la rutina ---
        st.subheader("📋 Tabla de la Rutina de Ejercicios")
        df_rutina = pd.read_excel(archivo_path, engine="odf", sheet_name="Rutina")
        df_rutina_limpia = df_rutina.dropna(subset=["Ejercicio"])
        st.dataframe(df_rutina_limpia)

        # --- Gráficos filtrables por Día y Grupo Muscular ---
        st.subheader("📊 Visualización Filtrada de la Rutina de Entrenamiento")

        if not df_rutina_limpia.empty:
            dias = df_rutina_limpia["Día"].dropna().unique()
            dia_seleccionado = st.selectbox("Seleccioná un día de entrenamiento", sorted(dias))

            grupos = df_rutina_limpia[df_rutina_limpia["Día"] == dia_seleccionado]["Grupo Muscular"].dropna().unique()
            grupo_seleccionado = st.selectbox("Seleccioná un grupo muscular", sorted(grupos))

            ejercicios = df_rutina_limpia[
                (df_rutina_limpia["Día"] == dia_seleccionado) &
                (df_rutina_limpia["Grupo Muscular"] == grupo_seleccionado)
            ]

            st.markdown(f"### Ejercicios para **{grupo_seleccionado}** el día **{dia_seleccionado}**")

            for _, row in ejercicios.iterrows():
                ejercicio = row["Ejercicio"]
                valores = row[["Series", "Repeticiones", "Peso (kg)", "Descanso (min)"]]

                if valores.notnull().all():
                    st.markdown(f"**{ejercicio}**")
                    fig, ax = plt.subplots(figsize=(6, 3))
                    valores.plot(kind="bar", ax=ax, color=["steelblue", "orange", "green", "red"])
                    ax.set_ylabel("Valor")
                    ax.set_xticklabels(valores.index, rotation=45)
                    ax.set_title("")
                    ax.grid(True)
                    st.pyplot(fig)

    else:
        st.error("❌ No se encontró un archivo para ese ID. Verificá el código ingresado o consultá con tu entrenador.")
