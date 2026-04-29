import streamlit as st
import pandas as pd
from PIL import Image
import os

# Configuración de la página
st.set_page_config(page_title="Geología DB", layout="wide")

st.title("🪨 Gestor de Muestras Geológicas")

# 1. Cargar o crear la base de datos
FILE_DB = "muestras.csv"

if os.path.exists(FILE_DB):
    df = pd.read_csv(FILE_DB)
else:
    # Si no existe, creamos una estructura básica
    df = pd.DataFrame(columns=["ID", "Nombre", "Tipo", "Lugar", "Fecha", "Imagen_URL"])

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Búsqueda")
buscar = st.sidebar.text_input("Buscar por nombre o ID")
tipo_filtro = st.sidebar.multiselect("Filtrar por Tipo", df["Tipo"].unique())

# Aplicar filtros
df_filtrado = df.copy()
if buscar:
    df_filtrado = df_filtrado[df_filtrado['Nombre'].str.contains(buscar, case=False)]
if tipo_filtro:
    df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipo_filtro)]

# --- CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["📊 Visualización y Filtros", "➕ Añadir Nuevo Registro"])

with tab1:
    st.subheader("Registros Actuales")
    # Tabla editable: permite cambiar datos directamente
    df_editado = st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")
    
    if st.button("Guardar Cambios en la Tabla"):
        df_editado.to_csv(FILE_DB, index=False)
        st.success("¡Base de datos actualizada!")

with tab2:
    st.subheader("Nuevo Registro")
    with st.form("formulario_nuevo"):
        col1, col2 = st.columns(2)
        with col1:
            nuevo_id = st.text_input("ID de la muestra")
            nuevo_nombre = st.text_input("Nombre de la roca")
            nuevo_tipo = st.selectbox("Tipo", ["Ígnea", "Sedimentaria", "Metamórfica", "Otro"])
        with col2:
            nuevo_lugar = st.text_input("Lugar de toma")
            nueva_fecha = st.date_input("Fecha")
            nueva_imagen = st.file_uploader("Subir Imagen", type=["jpg", "png", "jpeg"])
        
        enviar = st.form_submit_button("Registrar Roca")
        
        if enviar:
            # Aquí podrías guardar la imagen localmente o en la nube
            # Por ahora, simulamos el registro
            nueva_fila = pd.DataFrame([{
                "ID": nuevo_id, "Nombre": nuevo_nombre, "Tipo": nuevo_tipo,
                "Lugar": nuevo_lugar, "Fecha": str(nueva_fecha), "Imagen_URL": "ver_foto"
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)
            df.to_csv(FILE_DB, index=False)
            st.success("Muestra añadida con éxito.")