import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN DE LA APP
# Esto define el título de la pestaña y que la app ocupe todo el ancho de la pantalla
st.set_page_config(page_title="NaturaCanaria Pro", layout="wide")

st.title("🌿 NaturaCanaria Pro")
st.subheader("Base de datos científica de Biodiversidad Canaria")

# 2. BASE DE DATOS INTERNA (El Inventario)
# Aquí es donde añadiremos todas las especies. 
# 'Lat' y 'Lon' son las coordenadas reales de donde suelen estar.
@st.cache_data
def cargar_datos():
    especies = [
        {
            "Nombre": "Pinzón Azul",
            "Cientifico": "Fringilla teydea",
            "Reino": "Fauna",
            "Tipo": "Aves",
            "Origen": "Endémica",
            "Color": "Azul",
            "Lat": 28.27, "Lon": -16.64,
            "Descripcion": "Ave emblemática de Tenerife, vive en los pinares de alta montaña."
        },
        {
            "Nombre": "Tajinaste Rojo",
            "Cientifico": "Echium wildpretii",
            "Reino": "Flora",
            "Tipo": "Arbustiva",
            "Origen": "Endémica",
            "Color": "Rojo",
            "Lat": 28.21, "Lon": -16.62,
            "Descripcion": "Planta espectacular que florece en el Teide durante la primavera."
        },
        {
            "Nombre": "Lagarto Gigante",
            "Cientifico": "Gallotia simonyi",
            "Reino": "Fauna",
            "Tipo": "Reptiles",
            "Origen": "Endémica",
            "Color": "Marrón/Negro",
            "Lat": 27.75, "Lon": -18.03,
            "Descripcion": "Uno de los reptiles más raros del mundo, propio de El Hierro."
        }
    ]
    return pd.DataFrame(especies)

df = cargar_datos()

# 3. BUSCADOR DE IMÁGENES AUTOMÁTICO
# Esta función va a Wikipedia, busca el nombre científico y trae la foto real.
def obtener_foto_real(nombre_cientifico):
    try:
        api_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{nombre_cientifico.replace(' ', '_')}"
        res = requests.get(api_url).json()
        return res.get('thumbnail', {}).get('source', "https://via.placeholder.com/400")
    except:
        return "https://via.placeholder.com/400"

# 4. INTERFAZ DE USUARIO (Barra Lateral)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2913/2913520.png", width=100)
st.sidebar.header("Filtros Avanzados")

# Filtro por Reino
filtro_reino = st.sidebar.radio("Reino", ["Todos", "Flora", "Fauna"])

# Filtro por Color (Para Flora)
colores_disponibles = ["Todos"] + list(df['Color'].unique())
filtro_color = st.sidebar.selectbox("Filtrar por Color de Flor", colores_disponibles)

# Lógica de filtrado
df_filtrado = df
if filtro_reino != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Reino'] == filtro_reino]
if filtro_color != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Color'] == filtro_color]

# 5. CUERPO PRINCIPAL (Pestañas)
tab_cat, tab_map, tab_reg = st.tabs(["📚 Catálogo", "🗺️ Mapa Real", "📸 Mi Registro"])

with tab_cat:
    # Mostramos las tarjetas de cada especie
    for index, row in df_filtrado.iterrows():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(obtener_foto_real(row['Cientifico']), caption=row['Nombre'])
        with col2:
            st.write(f"### {row['Nombre']}")
            st.write(f"**Nombre Científico:** *{row['Cientifico']}*")
            st.write(f"**Estatus:** {row['Origen']} | **Tipo:** {row['Tipo']}")
            st.write(row['Descripcion'])
        st.divider()

with tab_map:
    st.write("### Mapa de Abundancia")
    st.write("Los puntos indican zonas de alta probabilidad de avistamiento.")
    
    # Crear el mapa centrado en Canarias
    m = folium.Map(location=[28.29, -16.6], zoom_start=8)
    
    # Añadir los puntos de las especies al mapa
    for i, row in df_filtrado.iterrows():
        color_punto = 'green' if row['Reino'] == 'Flora' else 'blue'
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=f"<b>{row['Nombre']}</b><br>{row['Cientifico']}",
            icon=folium.Icon(color=color_punto, icon='leaf' if row['Reino'] == 'Flora' else 'info-sign')
        ).add_to(m)
    
    st_folium(m, width=1000, height=500)

with tab_reg:
    st.write("### Registrar Nuevo Avistamiento")
    # Formulario para que el usuario suba sus cosas
    with st.form("registro"):
        nombre_usu = st.text_input("¿Qué has visto?")
        foto_usu = st.file_uploader("Sube tu foto", type=['jpg', 'png'])
        comentarios = st.text_area("Notas (donde estaba, comportamiento...)")
        enviar = st.form_submit_button("Guardar Avistamiento")
        
        if enviar:
            st.success(f"¡Gracias! Tu registro de '{nombre_usu}' ha sido guardado en la base de datos.")
