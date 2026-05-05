import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTILO PREMIUM)
st.set_page_config(
    page_title="NaturaCanaria Pro | Biodiversidad",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de CSS Avanzado para Diseño Responsivo y Estético
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Lato:wght@300;400&display=swap');

    /* Variables de Color */
    :root {
        --primary: #1B5E20;
        --secondary: #2E7D32;
        --accent: #FFC107;
        --bg: #F8F9FA;
    }

    .main { background-color: var(--bg); font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; color: var(--primary); }

    /* Tarjetas de Especies (Grid Premium) */
    .species-card {
        background: white;
        padding: 0px;
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid #E0E0E0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        margin-bottom: 25px;
    }
    .species-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
    }
    .species-img-container {
        width: 100%;
        height: 200px;
        overflow: hidden;
    }
    .species-img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    .species-card:hover img { transform: scale(1.1); }
    
    .card-content { padding: 20px; }
    .island-tag {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    /* Tabs Personalizados */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #EEE; padding: 5px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        color: #555;
        border: none;
        background: none;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        color: var(--primary) !important;
    }

    /* Formulario de Registro */
    .stForm {
        background: white;
        padding: 30px;
        border-radius: 20px;
        border: none;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }

    /* Ajustes Móviles */
    @media (max-width: 768px) {
        .species-img-container { height: 180px; }
        h1 { font-size: 2rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE DATOS INTELIGENTE
@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv('especies.csv')
        df.columns = df.columns.str.strip()
        return df
    except:
        # Datos Core de Referencia (Coordenadas en Tierra)
        return pd.DataFrame([
            {"Nombre": "Pinzón Azul", "Cientifico": "Fringilla teydea", "Grupo": "Aves", "Isla": "Tenerife", "Lat": 28.27, "Lon": -16.64, "Desc": "Símbolo de los bosques de pinar de Tenerife."},
            {"Nombre": "Lagarto Gigante", "Cientifico": "Gallotia simonyi", "Grupo": "Reptiles", "Isla": "El Hierro", "Lat": 27.75, "Lon": -18.03, "Desc": "Especie protegida, símbolo de la isla del Meridiano."},
            {"Nombre": "Drago Milenario", "Cientifico": "Dracaena draco", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.36, "Lon": -16.72, "Desc": "Árbol milenario de gran valor botánico."},
            {"Nombre": "Tajinaste Rojo", "Cientifico": "Echium wildpretii", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.21, "Lon": -16.62, "Desc": "Especie única de las cumbres tinerfeñas."}
        ])

df = load_data()

# 3. MOTOR DE BÚSQUEDA DE IMÁGENES (ALTA DISPONIBILIDAD)
@st.cache_data(ttl=3600)
def fetch_image(scientific_name):
    # Header profesional para evitar bloqueos de Wikipedia
    headers = {'User-Agent': 'NaturaCanariaPremium/2.0'}
    name = scientific_name.replace(' ', '_')
    try:
        # Intento 1: API de Resumen (Español)
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{name}"
        data = requests.get(url, headers=headers, timeout=5).json()
        if 'thumbnail' in data: return data['thumbnail']['source']
        
        # Intento 2: Wikipedia Global (Inglés)
        url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
        data_en = requests.get(url_en, headers=headers, timeout=5).json()
        if 'thumbnail' in data_en: return data_en['thumbnail']['source']
    except: pass
    return "https://images.unsplash.com/photo-1518173946687-a4c8a9ba332f?q=80&w=400&auto=format&fit=crop"

# 4. INTERFAZ DE USUARIO (DASHBOARD)
st.title("🌿 NaturaCanaria Pro")
st.markdown("<p style='font-size:1.2rem; color:#666;'>Plataforma Inteligente de Biodiversidad Canaria</p>", unsafe_allow_html=True)

# Pestañas principales
tabs = st.tabs(["🏛️ Enciclopedia", "🌍 Mapa Interactivo", "📷 Registro de Campo"])

# --- PESTAÑA 1: ENCICLOPEDIA ---
with tabs[0]:
    st.markdown("### Catálogo de Especies")
    search_col, filter_col = st.columns([2,1])
    with search_col:
        query = st.text_input("Buscar especie...", placeholder="Ej: Pinzón azul, Reptiles...")
    with filter_col:
        filtro_isla = st.selectbox("Filtrar por isla", ["Todas"] + sorted(df['Isla'].unique().tolist()))

    filtered_df = df.copy()
    if query:
        filtered_df = filtered_df[filtered_df['Nombre'].str.contains(query, case=False) | filtered_df['Grupo'].str.contains(query, case=False)]
    if filtro_isla != "Todas":
        filtered_df = filtered_df[filtered_df['Isla'] == filtro_isla]

    # Agrupación por Categorías
    for cat in sorted(filtered_df['Grupo'].unique()):
        with st.expander(f"📁 {cat.upper()}", expanded=True):
            cat_df = filtered_df[filtered_df['Grupo'] == cat]
            # Grid Responsivo: 4 columnas en PC, se adapta a 1 en móvil
            cols = st.columns([1,1,1,1])
            for idx, (_, row) in enumerate(cat_df.iterrows()):
                with cols[idx % 4]:
                    img_url = fetch_image(row['Cientifico'])
                    st.markdown(f"""
                        <div class="species-card">
                            <div class="species-img-container">
                                <img src="{img_url}">
                            </div>
                            <div class="card-content">
                                <span class="island-tag">{row['Isla']}</span>
                                <h3 style="margin:5px 0 0 0; font-size:1.2rem;">{row['Nombre']}</h3>
                                <p style="font-style:italic; color:#777; font-size:0.85rem; margin-bottom:10px;">{row['Cientifico']}</p>
                                <p style="font-size:0.9rem; line-height:1.4;">{row['Desc']}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# --- PESTAÑA 2: MAPA INTERACTIVO ---
with tabs[1]:
    st.markdown("### Distribución Real de Especies")
    st.info("Utilice el zoom para explorar los hábitats exactos en las islas.")
    
    # Mapa optimizado con OpenStreetMap (Sin errores)
    m = folium.Map(location=[28.3, -15.8], zoom_start=7, tiles="OpenStreetMap")
    
    for _, row in df.iterrows():
        # Lógica de colores por grupo
        color = 'green' if row['Grupo'] == 'Flora' else 'blue'
        icon = 'leaf' if row['Grupo'] == 'Flora' else 'eye-open'
        
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=folium.Popup(f"<b>{row['Nombre']}</b><br>{row['Cientifico']}", max_width=300),
            tooltip=row['Nombre'],
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
    
    st_folium(m, width="100%", height=600)

# --- PESTAÑA 3: REGISTRO DE CAMPO ---
with tabs[2]:
    col_f1, col_f2 = st.columns([1,1])
    with col_f1:
        st.markdown("### Registro de Avistamiento")
        st.write("Colabora con la base de datos registrando tus encuentros con la naturaleza.")
        
        with st.form("registry_form", clear_on_submit=True):
            obs_name = st.text_input("¿Qué especie has visto?")
            obs_island = st.selectbox("Isla del avistamiento", ["Tenerife", "Gran Canaria", "La Palma", "La Gomera", "El Hierro", "Fuerteventura", "Lanzarote", "La Graciosa"])
            obs_file = st.file_uploader("Subir evidencia fotográfica", type=['jpg', 'jpeg', 'png'])
            obs_note = st.text_area("Notas de campo (comportamiento, ubicación exacta...)")
            
            submitted = st.form_submit_button("Finalizar Registro")
            if submitted:
                if obs_name:
                    st.balloons()
                    st.success(f"¡Avistamiento de **{obs_name}** registrado! Gracias por tu colaboración científica.")
                else:
                    st.error("Por favor, introduce el nombre de la especie.")
    
    with col_f2:
        st.markdown("### Tus estadísticas")
        st.metric(label="Especies Catalogadas", value=len(df), delta="Activo")
        st.write("Cada registro ayuda a proteger nuestro ecosistema único.")
        st.image("https://images.unsplash.com/photo-1518173946687-a4c8a9ba332f?q=80&w=400&auto=format&fit=crop", caption="Unidos por la naturaleza canaria.")


