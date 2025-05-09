import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')  # Usar un backend sin interfaz gráfica
import matplotlib.pyplot as plt

# Titulo de la aplicación
st.title("Evolucion plan rutina entrenamiento")

# Subir archivo
uploaded_file = st.file_uploader("Sube tu archivo de progreso (.ods)", type=["ods"])

if uploaded_file is not None:
    # Leer el archivo subido
    df = pd.read_excel(uploaded_file, engine="odf", sheet_name="Medidas")

    # Procesar los datos
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df.set_index("Fecha", inplace=True)

    # Mostrar tabla de medidas
    st.subheader("Tabla de Medidas")
    st.dataframe(df)

    # Graficar medidas
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
    st.subheader("Evolución de Todas las Medidas")
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

