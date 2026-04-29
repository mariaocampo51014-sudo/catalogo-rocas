import streamlit as st
import pandas as pd
import requests
import time

# Configuración de la página
st.set_page_config(page_title="Catálogo Geológico Pro", layout="wide", page_icon="🪨")

# --- TUS ENLACES CONFIGURADOS ---
# Enlace de lectura (Corregido a formato CSV)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSfftWyw3WPs2AyLKMs45ISL3CnuoJ6g9i782185Zgtxa01YrxKtT7JZIrUVmvE75adawKwurAIZ6XW/pub?output=csv"

# Enlace de escritura (Tu Aplicación Web /exec)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxnEVxAJCUmdI4Grt06vjb3KS1TgtdCE59I5blyiiBtElLaloGpHFjGl2eSpU3XrF8C/exec"

def cargar_datos():
    try:
        # Forzamos la descarga de datos frescos evitando el cache
        url_fresca = f"{URL_CSV}&cache_bust={int(time.time())}"
        return pd.read_csv(url_fresca)
    except:
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
                
                if pd.notna(roca["IMAGEN"]) and str(roca["IMAGEN"]).startswith("http"):
                    st.image(roca["IMAGEN"], use_container_width=True)
                else:
                    st.info("No hay imagen o el link es inválido.")
                
                st.write(f"**📍 Lugar:** {roca['LUGAR']}")
                st.write(f"**📏 Tamaño:** {roca['TAMAÑO']}")
    else:
        st.warning("Aún no hay datos. Agrega la primera roca en la pestaña 'Registrar Muestra'.")

with tab_añadir:
    st.subheader("Nuevo Registro")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_id = st.text_input("ID")
            f_nom = st.text_input("Nombre de la Muestra")
            f_tam = st.text_input("Tamaño (ej: 5cm)")
        with col2:
            f_lug = st.text_input("Lugar de Origen")
            f_fec = st.date_input("Fecha")
            f_img = st.text_input("Link de Imagen (URL)")
        
        if st.form_submit_button("🚀 Guardar en Google Sheets"):
            datos = {
                "ID": f_id, "TAMAÑO": f_tam, "MUESTRA": f_nom,
                "LUGAR": f_lug, "FECHA": str(f_fec), "IMAGEN": f_img
            }
            try:
                res = requests.post(URL_SCRIPT, json=datos)
                if res.status_code == 200:
                    st.success("¡Registrado correctamente! Refresca la página en unos segundos.")
                else:
                    st.error("Error al conectar con el Script.")
            except:
                st.error("Error de red.")