import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Geológico Pro", layout="wide", page_icon="🪨")

# 2. CONEXIÓN A GOOGLE SHEETS
def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        if "gcp_service_account" in st.secrets:
            # Configuración para la WEB (Streamlit Cloud)
            creds_info = dict(st.secrets["gcp_service_account"])
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
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

worksheet = conectar_google_sheets()

# 3. CARGA DE DATOS
def cargar_datos():
    if worksheet:
        try:
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df = cargar_datos()

# 4. INTERFAZ
st.title("🪨 Sistema de Gestión Geológica Colaborativo")
st.markdown("---")

tab_ver, tab_añadir = st.tabs(["🔍 Explorar Inventario", "➕ Registrar Muestra"])

# --- PESTAÑA 1: EXPLORAR ---
with tab_ver:
    if not df.empty:
        st.sidebar.header("Filtros")
        busqueda = st.sidebar.text_input("Buscar por Género o Localidad")
        
        df_f = df.copy()
        if busqueda:
            df_f = df[
                df['GENERO ESPECIE'].astype(str).str.contains(busqueda, case=False, na=False) | 
                df['LOCALIDAD'].astype(str).str.contains(busqueda, case=False, na=False)
            ]

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
                
                # Intentar mostrar la imagen desde el link de GitHub
                url_foto = roca.get("FOTO", "")
                if url_foto and str(url_foto).startswith("http"):
                    st.image(url_foto, caption=f"Muestra: {sel}", use_container_width=True)
                else:
                    st.info("No hay imagen disponible para esta muestra.")
                
                st.write(f"**📍 Localidad:** {roca['LOCALIDAD']}")
                st.write(f"**🪨 Litología:** {roca['LITOLOGIA']}")
    else:
        st.warning("Conectando con la base de datos...")

# --- PESTAÑA 2: AÑADIR ---
with tab_añadir:
    st.subheader("➕ Registrar Nueva Muestra")
    
    with st.form("form_registro", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_gen = st.text_input("GENERO ESPECIE")
            f_num = st.text_input("NUMERO EN COLECCIÓNN")
            f_uni = st.text_input("UNIDAD ESTRATIGRAFICA")
        with c2:
            f_loc = st.text_input("LOCALIDAD")
            f_lit = st.text_input("LITOLOGIA")
            f_eda = st.text_input("EDAD")
        with c3:
            f_cx = st.text_input("COORDENADA X")
            f_cy = st.text_input("COORDENADA Y")
            f_fec = st.date_input("FECHA RECOLECCION", datetime.date.today())

        f_cla = st.text_input("CLADO - CLASIFICACION")
        f_aso = st.text_input("ASOCIACION PALEONTOLOGICA")
        f_fos = st.text_input("TIPO DE FOSILIZACION")
        f_col = st.text_input("COLECTOR")
        f_cls = st.text_input("CLASIFICÓ")

        st.markdown("---")
        st.write("📷 **Fotografía de la muestra**")
        col_cam, _ = st.columns([0.4, 0.6]) 
        with col_cam:
            img_file = st.camera_input("Capturar", label_visibility="collapsed")
        
        enviar = st.form_submit_button("🚀 GUARDAR REGISTRO")

        if enviar:
            if f_gen and f_num:
                link_foto = ""
                
                # LÓGICA PARA GUARDAR LA IMAGEN
                if img_file:
                    # Crear carpeta si no existe
                    if not os.path.exists("fotos"):
                        os.makedirs("fotos")
                    
                    # Nombre de archivo único
                    nombre_archivo = f"fotos/{f_gen}_{f_num}.png"
                    with open(nombre_archivo, "wb") as f:
                        f.write(img_file.getbuffer())
                    
                    # Link directo al archivo en tu GitHub
                    link_foto = f"https://raw.githubusercontent.com/mariaocampo51014-sudo/catalogo-rocas/main/{nombre_archivo}"
                
                nueva_fila = [
                    f_gen, f_num, f_cx, f_cy, f_uni, f_loc, f_lit, 
                    f_eda, f_cla, f_aso, f_fos, f_col, str(f_fec), f_cls, link_foto
                ]
                
                try:
                    worksheet.append_row(nueva_fila)
                    st.success("✅ Datos enviados. ¡Recuerda hacer PUSH en VS Code para subir la foto!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
            else:
                st.warning("⚠️ Género y Número son obligatorios.")