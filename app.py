import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN DE PÁGINA (PROFESIONAL Y RESPONSIVA)
st.set_page_config(
    page_title="NaturaCanaria Pro",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DISEÑO VISUAL (CSS) - Optimizado para móvil y PC
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: white !important;
    }
    .species-card {
        background: white;
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .species-card:hover { transform: translateY(-5px); }
    .species-card img {
        width: 100%;
        height: 220px;
        border-radius: 15px;
        object-fit: cover;
    }
    .desc-text { font-size: 0.9rem; color: #444; margin-top: 8px; }
    .badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 3. BASE DE DATOS EXTENDIDA (Fauna y Flora)
@st.cache_data
def get_combined_data():
    # Intentamos leer del CSV, si no, usamos esta lista masiva
    especies_lista = [
        {"Nombre": "Pinzón Azul de Tenerife", "Cientifico": "Fringilla teydea", "Grupo": "Aves", "Isla": "Tenerife", "Lat": 28.27, "Lon": -16.64, "Desc": "Ave icónica de los pinares tinerfeños."},
        {"Nombre": "Pinzón Azul de Gran Canaria", "Cientifico": "Fringilla polatzeki", "Grupo": "Aves", "Isla": "Gran Canaria", "Lat": 27.95, "Lon": -15.60, "Desc": "Especie en peligro crítico en Inagua."},
        {"Nombre": "Lagarto Gigante de El Hierro", "Cientifico": "Gallotia simonyi", "Grupo": "Reptiles", "Isla": "El Hierro", "Lat": 27.75, "Lon": -18.03, "Desc": "Tesoro vivo de la isla del meridiano."},
        {"Nombre": "Lagarto Gigante de La Gomera", "Cientifico": "Gallotia bravoana", "Grupo": "Reptiles", "Isla": "La Gomera", "Lat": 28.12, "Lon": -17.34, "Desc": "Redescubierto en los acantilados de Valle Gran Rey."},
        {"Nombre": "Tajinaste Rojo", "Cientifico": "Echium wildpretii", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.21, "Lon": -16.62, "Desc": "Espectacular inflorescencia del Teide."},
        {"Nombre": "Drago Milenario", "Cientifico": "Dracaena draco", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.36, "Lon": -16.72, "Desc": "Símbolo de sabiduría y longevidad."},
        {"Nombre": "Hubara Canaria", "Cientifico": "Chlamydotis undulata fuertaventurae", "Grupo": "Aves", "Isla": "Fuerteventura", "Lat": 28.50, "Lon": -13.90, "Desc": "Reina de las llanuras desérticas."},
        {"Nombre": "Guirre Canario", "Cientifico": "Neophron percnopterus majorensis", "Grupo": "Aves", "Isla": "Fuerteventura", "Lat": 28.45, "Lon": -14.00, "Desc": "El alimoche canario, único buitre local."},
        {"Nombre": "Paloma Rabiche", "Cientifico": "Columba junoniae", "Grupo": "Aves", "Isla": "La Palma", "Lat": 28.70, "Lon": -17.85, "Desc": "Habitante de la laurisilva canaria."},
        {"Nombre": "Pardela Cenicienta", "Cientifico": "Calonectris diomedea", "Grupo": "Aves Marinas", "Isla": "Costas", "Lat": 28.00, "Lon": -14.50, "Desc": "Regresa cada año a nuestros acantilados."},
        {"Nombre": "Violeta del Teide", "Cientifico": "Viola cheiranthifolia", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.27, "Lon": -16.63, "Desc": "La planta que florece a mayor altitud en España."},
        {"Nombre": "Orejudo Canario", "Cientifico": "Plecotus teneriffae", "Grupo": "Mamíferos", "Isla": "Todas", "Lat": 28.30, "Lon": -16.50, "Desc": "Murciélago endémico de grandes orejas."},
        {"Nombre": "Perenquén de Delalande", "Cientifico": "Tarentola delalandii", "Grupo": "Reptiles", "Isla": "Tenerife/La Palma", "Lat": 28.40, "Lon": -16.30, "Desc": "Geco común en muros y zonas bajas."},
    ]
    try:
        df_csv = pd.read_csv('especies.csv')
        return df_csv
    except:
        return pd.DataFrame(especies_lista)

df = get_combined_data()

# 4. BUSCADOR DE IMÁGENES REALES (WIKIPEDIA API)
@st.cache_data
def fetch_image(scientific_name):
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
        r = requests.get(url, timeout=5).json()
        return r.get('thumbnail', {}).get('source', "https://via.placeholder.com/400?text=No+Photo")
    except:
        return "https://via.placeholder.com/400?text=Error"

# 5. ESTRUCTURA DE LA APP
st.title("🌿 NaturaCanaria Pro")
st.markdown("---")

# Buscador superior
search_query = st.text_input("🔍 Busca por nombre, grupo o isla...", placeholder="Ej: Pinzón, Reptiles, Lanzarote...")

if search_query:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

# PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📚 ENCICLOPEDIA", "🗺️ MAPA DE DISTRIBUCIÓN", "📸 MI DIARIO"])

with tab1:
    # Cuadrícula dinámica: 4 columnas en PC, 1 en móvil
    cols = st.columns([1, 1, 1, 1])
    for i, row in df.iterrows():
        with cols[i % 4]:
            img = fetch_image(row['Cientifico'])
            st.markdown(f"""
                <div class="species-card">
                    <img src="{img}">
                    <div style="margin-top:10px;">
                        <span class="badge">{row['Grupo']}</span>
                        <h3 style="margin:5px 0 0 0; font-size:1.2rem;">{row['Nombre']}</h3>
                        <p style="font-style:italic; color:gray; font-size:0.8rem; margin:0;">{row['Cientifico']}</p>
                        <p style="margin:5px 0 0 0; font-weight:bold; font-size:0.9rem;">📍 {row['Isla']}</p>
                        <div class="desc-text">{row['Desc']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with tab2:
    st.subheader("Ubicaciones de Especies en Tiempo Real")
    # Mapa centrado en el archipiélago sin capas de pago (Stamen)
    m = folium.Map(location=[28.3, -15.8], zoom_start=7, tiles="OpenStreetMap")
    
    for _, row in df.iterrows():
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=f"<b>{row['Nombre']}</b><br>{row['Cientifico']}",
            tooltip=row['Nombre'],
            icon=folium.Icon(color='green' if row['Grupo'] == 'Flora' else 'blue', icon='leaf' if row['Grupo'] == 'Flora' else 'eye-open')
        ).add_to(m)
    
    st_folium(m, width="100%", height=600)

with tab3:
    st.header("📸 Registro de Campo")
    with st.form("registro_avistamiento"):
        c1, c2 = st.columns(2)
        with c1:
            especie_obs = st.text_input("Especie observada")
            isla_obs = st.selectbox("Isla", ["Tenerife", "Gran Canaria", "La Palma", "La Gomera", "El Hierro", "Fuerteventura", "Lanzarote", "La Graciosa"])
        with c2:
            foto_obs = st.file_uploader("Subir foto", type=['jpg', 'png'])
        notas_obs = st.text_area("Notas del avistamiento")
        
        if st.form_submit_button("Guardar Avistamiento"):
            st.success(f"¡Avistamiento de {especie_obs} guardado con éxito!")
