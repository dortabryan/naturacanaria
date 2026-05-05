import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN TOTAL Y ESTILO
st.set_page_config(page_title="NaturaCanaria Pro", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f8e9; border-radius: 10px; padding: 8px 16px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #388e3c !important; color: white !important; }
    .species-card {
        background: white; padding: 15px; border-radius: 15px;
        border: 1px solid #ddd; margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .species-card img {
        width: 100%; height: 220px; border-radius: 10px; object-fit: cover;
    }
    .category-box {
        border-left: 5px solid #388e3c; padding-left: 15px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS (CSV + EMERGENCIA)
@st.cache_data
def load_full_data():
    try:
        # Intentamos cargar tu archivo de GitHub
        df = pd.read_csv('especies.csv')
        # Limpieza básica por si hay espacios en los nombres
        df.columns = df.columns.str.strip()
        return df
    except:
        # Si el CSV falla, estos son los datos que verás (asegúrate de que el CSV esté bien)
        return pd.DataFrame([
            {"Nombre": "Pinzón Azul", "Cientifico": "Fringilla teydea", "Grupo": "Aves", "Isla": "Tenerife", "Lat": 28.27, "Lon": -16.64, "Desc": "Vive en el pinar."},
            {"Nombre": "Tajinaste Rojo", "Cientifico": "Echium wildpretii", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.21, "Lon": -16.62, "Desc": "Cumbre del Teide."},
            {"Nombre": "Lagarto Gigante", "Cientifico": "Gallotia simonyi", "Grupo": "Reptiles", "Isla": "El Hierro", "Lat": 27.75, "Lon": -18.03, "Desc": "Especie protegida."},
            {"Nombre": "Hubara Canaria", "Cientifico": "Chlamydotis undulata", "Grupo": "Aves", "Isla": "Lanzarote", "Lat": 29.03, "Lon": -13.63, "Desc": "Zonas áridas."}
        ])

df = load_full_data()

# 3. BUSCADOR DE FOTOS REALES (WIKIPEDIA API)
@st.cache_data
def get_image(scientific_name, common_name):
    # Intento 1: Por nombre científico
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
        res = requests.get(url, timeout=3).json()
        if 'thumbnail' in res: return res['thumbnail']['source']
        
        # Intento 2: Por nombre común si el científico falla
        url_c = f"https://es.wikipedia.org/api/rest_v1/page/summary/{common_name.replace(' ', '_')}"
        res_c = requests.get(url_c, timeout=3).json()
        if 'thumbnail' in res_c: return res_c['thumbnail']['source']
    except:
        pass
    return "https://via.placeholder.com/400?text=Foto+Cargando..."

# 4. INTERFAZ DE LA APP
st.title("🌿 NaturaCanaria Pro")
st.write(f"Explorando {len(df)} especies categorizadas")

search = st.text_input("🔍 Buscar especie...", placeholder="Escribe el nombre de un animal o planta")
if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

tab1, tab2 = st.tabs(["🗂️ CATEGORÍAS", "📍 MAPA REAL"])

with tab1:
    # Agrupar automáticamente por la columna "Grupo" del CSV
    grupos = df['Grupo'].unique()
    for grupo in grupos:
        with st.expander(f"➕ {grupo.upper()}", expanded=True):
            sub_df = df[df['Grupo'] == grupo]
            # Creamos columnas (3 en PC, se vuelven 1 en móvil automáticamente)
            cols = st.columns(3)
            for i, (_, row) in enumerate(sub_df.iterrows()):
                with cols[i % 3]:
                    foto = get_image(str(row['Cientifico']), str(row['Nombre']))
                    st.markdown(f"""
                        <div class="species-card">
                            <img src="{foto}">
                            <h3 style="margin:10px 0 0 0; color:#2e7d32;">{row['Nombre']}</h3>
                            <p style="font-style:italic; color:#777; margin-bottom:5px;">{row['Cientifico']}</p>
                            <span style="background:#e8f5e9; padding:3px 8px; border-radius:5px; font-size:0.8em; font-weight:bold;">📍 {row['Isla']}</span>
                            <p style="margin-top:10px; font-size:0.9em;">{row['Desc']}</p>
                        </div>
                    """, unsafe_allow_html=True)

with tab2:
    st.subheader("Ubicación exacta en el Archipiélago")
    # Mapa centrado sin el error de Stamen
    m = folium.Map(location=[28.3, -15.8], zoom_start=7)
    
    for _, row in df.iterrows():
        # IMPORTANTE: El mapa lee las columnas "Lat" y "Lon" de tu CSV
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=f"<b>{row['Nombre']}</b>",
            tooltip=row['Nombre'],
            icon=folium.Icon(color='green', icon='leaf')
        ).add_to(m)
    
    st_folium(m, width="100%", height=550)
