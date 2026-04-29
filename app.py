import streamlit as st
import pandas as pd
import requests
import time

# Configuración de la página
st.set_page_config(page_title="Catálogo Geológico Pro", layout="wide", page_icon="🪨")

# --- TUS ENLACES CONFIGURADOS ---
# Enlace de lectura (CSV)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSfftWyw3WPs2AyLKMs45ISL3CnuoJ6g9i782185Zgtxa01YrxKtT7JZIrUVmvE75adawKwurAIZ6XW/pub?output=csv"

# Enlace de escritura (Tu Aplicación Web /exec)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxnEVxAJCUmdI4Grt06vjb3KS1TgtdCE59I5blyiiBtElLaloGpHFjGl2eSpU3XrF8C/exec"

def cargar_datos():
    try:
        # Forzamos la descarga de datos frescos evitando el cache
        url_fresca = f"{URL_CSV}&cache_bust={int(time.time())}"
        # Leemos el CSV y eliminamos espacios en blanco en los nombres de las columnas
        data = pd.read_csv(url_fresca)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

st.title("🪨 Sistema de Gestión Geológica Colaborativo")
st.markdown("---")

tab_ver, tab_añadir = st.tabs(["🔍 Explorar Inventario", "➕ Registrar Muestra"])

with tab_ver:
    if not df.empty:
        # Buscador en la barra lateral
        st.sidebar.header("Filtros")
        busqueda = st.sidebar.text_input("Buscar por nombre o lugar")
        
        # Lógica de filtrado
        df_f = df[df['MUESTRA'].str.contains(busqueda, case=False, na=False) | 
                  df['LUGAR'].str.contains(busqueda, case=False, na=False)] if busqueda else df

        col_tabla, col_detalle = st.columns([1.5, 1])
        
        with col_tabla:
            st.subheader("Registros")
            st.dataframe(df_f, use_container_width=True, hide_index=True)
        
        with col_detalle:
            st.subheader("Detalle Visual")
            if len(df_f) > 0:
                sel = st.selectbox("Ver detalle de:", df_f["MUESTRA"])
                roca = df_f[df_f["MUESTRA"] == sel].iloc[0]
                
                # --- CORRECCIÓN DEL ERROR DE IMAGEN ---
                # Buscamos la columna de imagen de forma segura
                col_img_nombre = "IMAGEN" 
                
                if col_img_nombre in roca:
                    url_foto = roca[col_img_nombre]
                    if pd.notna(url_foto) and str(url_foto).startswith("http"):
                        st.image(url_foto, use_container_width=True)
                    else:
                        st.info("No hay una imagen válida (URL) en Google Sheets para esta roca.")
                else:
                    st.error("No se encontró la columna 'IMAGEN'. Revisa los títulos en tu Google Sheets.")
                
                st.write(f"**📍 Lugar:** {roca['LUGAR']}")
                st.write(f"**📏 Tamaño:** {roca['TAMAÑO']}")
                st.write(f"**📅 Fecha:** {roca['FECHA']}")
    else:
        st.warning("La base de datos parece estar vacía o el formato de columnas es incorrecto.")

with tab_añadir:
    st.subheader("Nuevo Registro")
    st.write("Llena los campos para agregar una muestra a Google Sheets:")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_id = st.text_input("ID")
            f_nom = st.text_input("Nombre de la Muestra")
            f_tam = st.text_input("Tamaño (ej: 5cm)")
        with col2:
            f_lug = st.text_input("Lugar de Origen")
            f_fec = st.date_input("Fecha")
            f_img = st.text_input("Link de Imagen (URL directa)")
        
        if st.form_submit_button("🚀 Guardar en Google Sheets"):
            if f_nom and f_id:
                datos = {
                    "ID": f_id, "TAMAÑO": f_tam, "MUESTRA": f_nom,
                    "LUGAR": f_lug, "FECHA": str(f_fec), "IMAGEN": f_img
                }
                try:
                    res = requests.post(URL_SCRIPT, json=datos)
                    if res.status_code == 200:
                        st.success("¡Registrado correctamente! Refresca la página en 10 segundos para ver los cambios.")
                    else:
                        st.error("Error al conectar con el Script de Google.")
                except:
                    st.error("Error de red al intentar guardar.")
            else:
                st.warning("Por favor, ingresa al menos el ID y el Nombre.")