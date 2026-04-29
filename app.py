import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Catálogo de Rocas Pro", layout="wide", page_icon="🪨")

# --- CONEXIÓN CON TU GOOGLE SHEETS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSfftWyw3WPs2AyLKMs45ISL3CnuoJ6g9i782185Zgtxa01YrxKtT7JZIrUVmvE75adawKwurAIZ6XW/pub?output=csv"

def cargar_datos():
    try:
        # Cargamos los datos desde el enlace de publicación
        return pd.read_csv(URL_CSV)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# Cargar la base de datos
df = cargar_datos()

st.title("🪨 Sistema de Gestión Geológica")
st.markdown("---")

if not df.empty:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros de Búsqueda")
    busqueda = st.sidebar.text_input("Buscar por nombre de muestra o lugar")
    
    # Aplicar filtros
    mask = df['MUESTRA'].str.contains(busqueda, case=False, na=False) | \
           df['LUGAR'].str.contains(busqueda, case=False, na=False)
    df_filtrado = df[mask]

    # --- CUERPO PRINCIPAL ---
    tab1, tab2 = st.tabs(["📊 Vista de Tabla", "🖼️ Galería de Detalles"])

    with tab1:
        st.subheader("Registros en la Base de Datos")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        st.info(f"Se han encontrado {len(df_filtrado)} registros.")

    with tab2:
        if len(df_filtrado) > 0:
            st.subheader("Identificación Visual")
            # Selector para elegir qué roca ver en detalle
            opciones = df_filtrado["MUESTRA"].tolist()
            seleccion = st.selectbox("Selecciona una muestra para inspeccionar:", opciones)
            
            # Obtener datos de la fila seleccionada
            roca = df_filtrado[df_filtrado["MUESTRA"] == seleccion].iloc[0]
            
            col_img, col_info = st.columns([1, 1])
            
            with col_img:
                # Verificamos si hay un link de imagen y si es válido
                url_foto = roca["IMAGEN"]
                if pd.notna(url_foto) and str(url_foto).startswith("http"):
                    st.image(url_foto, caption=f"Muestra: {seleccion}", use_container_width=True)
                else:
                    st.warning("⚠️ No hay una URL de imagen válida en Google Sheets para esta muestra.")
            
            with col_info:
                st.write(f"**🔢 ID de Registro:** {roca['ID']}")
                st.write(f"**📏 Tamaño Aproximado:** {roca['TAMAÑO']}")
                st.write(f"**📍 Ubicación de Origen:** {roca['LUGAR']}")
                st.write(f"**📅 Fecha de Ingreso:** {roca['FECHA']}")
                st.info("Para actualizar estos datos, edita tu archivo de Google Sheets y refresca esta página.")
        else:
            st.warning("No hay muestras que coincidan con tu búsqueda.")

else:
    st.error("La base de datos está vacía o el enlace no funciona. Revisa la publicación en Google Sheets.")