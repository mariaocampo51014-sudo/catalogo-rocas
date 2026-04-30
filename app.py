import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Geológico Pro", layout="wide", page_icon="🪨")

# 2. CONEXIÓN A GOOGLE SHEETS
def conectar_google_sheets():
    # Permisos necesarios para Drive y Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # IMPORTANTE: Para Streamlit Cloud/GitHub, usaremos st.secrets por seguridad
    # Si estás en local, seguirá buscando el archivo 'secretos.json'
    try:
        if "gcp_service_account" in st.secrets:
            # Configuración para la WEB (Streamlit Cloud)
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Configuración para LOCAL
            creds = ServiceAccountCredentials.from_json_keyfile_name('secretos.json', scope)
        
        client = gspread.authorize(creds)
        sheet_id = "1joVXzX3T_MznE8xo-jMSXSoLhz-U2j9V7g9K-J1R2_c"
        spreadsheet = client.open_by_key(sheet_id)
        return spreadsheet.worksheet("BasePrueba")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Inicializar conexión
worksheet = conectar_google_sheets()

# 3. FUNCIONES DE DATOS
def cargar_datos():
    if worksheet:
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

df = cargar_datos()

# 4. INTERFAZ DE USUARIO
st.title("🪨 Sistema de Gestión Geológica Colaborativo")
st.markdown("---")

tab_ver, tab_añadir = st.tabs(["🔍 Explorar Inventario", "➕ Registrar Muestra"])

# --- PESTAÑA EXPLORAR ---
with tab_ver:
    if not df.empty:
        st.sidebar.header("Filtros")
        busqueda = st.sidebar.text_input("Buscar por Género o Localidad")
        
        if busqueda:
            df_f = df[
                df['GENERO ESPECIE'].astype(str).str.contains(busqueda, case=False, na=False) | 
                df['LOCALIDAD'].astype(str).str.contains(busqueda, case=False, na=False)
            ]
        else:
            df_f = df

        col_tabla, col_detalle = st.columns([1.5, 1])
        
        with col_tabla:
            st.subheader("Registros en Tiempo Real")
            st.dataframe(df_f, use_container_width=True, hide_index=True)
        
        with col_detalle:
            st.subheader("Detalle Visual")
            if len(df_f) > 0:
                opciones = df_f["GENERO ESPECIE"].unique().tolist()
                sel = st.selectbox("Ver detalle de:", opciones)
                roca = df_f[df_f["GENERO ESPECIE"] == sel].iloc[0]
                
                url_foto = roca.get("FOTO", "")
                if url_foto and str(url_foto).startswith("http"):
                    st.image(url_foto, use_container_width=True)
                else:
                    st.info("No hay imagen vinculada (URL) para esta muestra.")
                
                st.write(f"**🔢 Número:** {roca['NUMERO EN COLECCION']}")
                st.write(f"**📍 Localidad:** {roca['LOCALIDAD']}")
                st.write(f"**🗺️ Coordenadas:** {roca['COORDENADA X']}, {roca['COORDENADA Y']}")
                st.write(f"**🪨 Litología:** {roca['LITOLOGIA']}")
                st.write(f"**📅 Fecha:** {roca['FECHA RECOLECCION']}")
    else:
        st.warning("La base de datos está vacía o no se pudo conectar.")

# --- PESTAÑA AÑADIR (CON CÁMARA PEQUEÑA AL FINAL) ---
with tab_añadir:
    st.subheader("➕ Registrar Nueva Muestra")
    
    with st.form("form_registro", clear_on_submit=True):
        # Bloque de datos principales
        c1, c2, c3 = st.columns(3)
        with c1:
            f_gen = st.text_input("GENERO ESPECIE")
            f_num = st.text_input("NUMERO EN COLECCION")
            f_uni = st.text_input("UNIDAD ESTRATIGRAFICA")
        with c2:
            f_loc = st.text_input("LOCALIDAD")
            f_lit = st.text_input("LITOLOGIA")
            f_eda = st.text_input("EDAD")
        with c3:
            f_cx = st.text_input("COORDENADA X")
            f_cy = st.text_input("COORDENADA Y")
            f_fec = st.date_input("FECHA RECOLECCION", datetime.date.today())

        # Bloque de clasificación adicional
        f_cla = st.text_input("CLADO - CLASIFICACION")
        f_aso = st.text_input("ASOCIACION PALEONTOLOGICA")
        f_fos = st.text_input("TIPO DE FOSILIZACION")
        f_col = st.text_input("COLECTOR")
        f_cls = st.text_input("CLASIFICÓ")

        st.markdown("---")
        
        # SECCIÓN DE FOTO PEQUEÑA AL FINAL
        st.write("📷 **Fotografía de la muestra**")
        col_cam, col_vacia = st.columns([0.4, 0.6]) # Cámara ocupa solo el 40% del ancho
        with col_cam:
            img_file = st.camera_input("Capturar", label_visibility="collapsed")
        
        enviar = st.form_submit_button("🚀 GUARDAR REGISTRO COMPLETO")

        if enviar:
            if f_gen and f_num:
                # Nota: El archivo de imagen vive en 'img_file'. 
                # Por ahora marcamos en el Excel que se tomó la foto.
                foto_status = "Foto capturada" if img_file else "Sin foto"
                
                nueva_fila = [
                    f_gen, f_num, f_cx, f_cy, f_uni, f_loc, f_lit, 
                    f_eda, f_cla, f_aso, f_fos, f_col, str(f_fec), f_cls, foto_status
                ]
                
                try:
                    worksheet.append_row(nueva_fila)
                    st.success("✅ ¡Registro exitoso en la nube!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
            else:
                st.warning("⚠️ El Género y el Número son obligatorios.")