import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN Y ESTILO AVANZADO
st.set_page_config(page_title="NaturaCanaria Pro", page_icon="🐬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background-color: #f4f7f6; }

    /* Botones de Categoría */
    .stButton > button {
        border-radius: 20px;
        height: 110px;
        width: 100%;
        background: white;
        color: #2e7d32;
        border: 2px solid #e8f5e9;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stButton > button:hover {
        background: #2e7d32;
        color: white;
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }

    /* Tarjetas de Especies */
    .species-card {
        background: white;
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid #eee;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .species-card img {
        width: 100%;
        height: 220px;
        object-fit: cover;
    }
    .card-info { padding: 20px; }
    .tag {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. BASE DE DATOS EXTENDIDA (MÁS ESPECIES)
@st.cache_data
def get_data():
    data = [
        # MARINOS
        {"Nombre": "Yubarta (Ballena)", "Cientifico": "Megaptera novaeangliae", "Grupo": "Marinos", "Isla": "Océano", "Lat": 28.2, "Lon": -16.9, "Desc": "Avistamientos frecuentes en sus rutas migratorias."},
        {"Nombre": "Delfín Mular", "Cientifico": "Tursiops truncatus", "Grupo": "Marinos", "Isla": "Todas", "Lat": 28.1, "Lon": -16.7, "Desc": "El delfín más común y amigable de nuestras costas."},
        {"Nombre": "Tiburón Ángel (Angelote)", "Cientifico": "Squatina squatina", "Grupo": "Marinos", "Isla": "Fondos arenosos", "Lat": 28.0, "Lon": -15.4, "Desc": "Canarias es uno de sus últimos refugios mundiales."},
        
        # ANFIBIOS
        {"Nombre": "Ranita de San Antonio", "Cientifico": "Hyla meridionalis", "Grupo": "Anfibios", "Isla": "Tenerife/Gran Canaria", "Lat": 28.4, "Lon": -16.3, "Desc": "Pequeña, verde y ruidosa en noches de lluvia."},
        {"Nombre": "Rana Común", "Cientifico": "Pelophylax perezi", "Grupo": "Anfibios", "Isla": "Todas", "Lat": 28.1, "Lon": -17.2, "Desc": "Muy común en estanques y canales de agua."},

        # GRANJA
        {"Nombre": "Cochino Negro", "Cientifico": "Sus scrofa", "Grupo": "Granja", "Isla": "Todas", "Lat": 28.3, "Lon": -16.4, "Desc": "Raza autóctona de gran importancia cultural."},
        {"Nombre": "Camello Canario", "Cientifico": "Camelus dromedarius", "Grupo": "Granja", "Isla": "Lanzarote/Fuerteventura", "Lat": 28.9, "Lon": -13.7, "Desc": "Fundamental históricamente para la agricultura."},
        {"Nombre": "Vaca Canaria", "Cientifico": "Bos taurus", "Grupo": "Granja", "Isla": "Tenerife", "Lat": 28.5, "Lon": -16.2, "Desc": "Raza rústica utilizada para el arrastre y labranza."},

        # AVES
        {"Nombre": "Pinzón Azul", "Cientifico": "Fringilla teydea", "Grupo": "Aves", "Isla": "Tenerife", "Lat": 28.2, "Lon": -16.6, "Desc": "Habitante exclusivo de los pinares canarios."},
        {"Nombre": "Hubara Canaria", "Cientifico": "Chlamydotis undulata", "Grupo": "Aves", "Isla": "Fuerteventura", "Lat": 28.4, "Lon": -14.1, "Desc": "Espectacular ave de las zonas desérticas."},

        # REPTILES
        {"Nombre": "Lagarto Gigante", "Cientifico": "Gallotia simonyi", "Grupo": "Reptiles", "Isla": "El Hierro", "Lat": 27.7, "Lon": -18.0, "Desc": "Tesoro prehistórico de la isla de El Hierro."},
        {"Nombre": "Perenquén Común", "Cientifico": "Tarentola delalandii", "Grupo": "Reptiles", "Isla": "Tenerife/La Palma", "Lat": 28.4, "Lon": -16.3, "Desc": "Geco nocturno que limpia de insectos nuestros hogares."},

        # FLORA
        {"Nombre": "Drago Milenario", "Cientifico": "Dracaena draco", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.3, "Lon": -16.7, "Desc": "Árbol sagrado de los antiguos pobladores."},
        {"Nombre": "Tajinaste Rojo", "Cientifico": "Echium wildpretii", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.2, "Lon": -16.6, "Desc": "La joya botánica del Parque Nacional del Teide."}
    ]
    return pd.DataFrame(data)

df = get_data()

# 3. BUSCADOR DE FOTOS
@st.cache_data
def get_img(sc):
    try:
        r = requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{sc.replace(' ', '_')}", timeout=3).json()
        return r.get('thumbnail', {}).get('source', "https://via.placeholder.com/400")
    except: return "https://via.placeholder.com/400"

# 4. INTERFAZ
st.title("🌿 NaturaCanaria Pro")

tabs = st.tabs(["🏛️ ENCICLOPEDIA", "🌍 MAPA", "📸 REGISTRO"])

# --- ENCICLOPEDIA CON ICONOS INTERACTIVOS ---
with tabs[0]:
    if 'cat' not in st.session_state: st.session_state.cat = None
    
    st.markdown("### Selecciona una categoría")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: 
        if st.button("🐬\nMARINOS"): st.session_state.cat = "Marinos"
    with c2: 
        if st.button("🐸\nANFIBIOS"): st.session_state.cat = "Anfibios"
    with c3: 
        if st.button("🚜\nGRANJA"): st.session_state.cat = "Granja"
    with c4: 
        if st.button("🐦\nAVES"): st.session_state.cat = "Aves"
    with c5: 
        if st.button("🦎\nREPTILES"): st.session_state.cat = "Reptiles"
    with c6: 
        if st.button("🌸\nFLORA"): st.session_state.cat = "Flora"

    if st.session_state.cat:
        st.divider()
        col_t, col_b = st.columns([3,1])
        col_t.markdown(f"## {st.session_state.cat}")
        if col_b.button("✖️ Cerrar"):
            st.session_state.cat = None
            st.rerun()

        sub = df[df['Grupo'] == st.session_state.cat]
        grid = st.columns(3)
        for i, (_, r) in enumerate(sub.iterrows()):
            with grid[i % 3]:
                foto = get_img(r['Cientifico'])
                st.markdown(f"""
                    <div class="species-card">
                        <img src="{foto}">
                        <div class="card-info">
                            <span class="tag">{r['Isla']}</span>
                            <h3 style="margin-top:10px;">{r['Nombre']}</h3>
                            <p style="font-style:italic; color:gray;">{r['Cientifico']}</p>
                            <p>{r['Desc']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# --- MAPA ---
with tabs[1]:
    m = folium.Map(location=[28.3, -15.8], zoom_start=7)
    for _, r in df.iterrows():
        folium.Marker([r['Lat'], r['Lon']], popup=r['Nombre'], icon=folium.Icon(color='green', icon='leaf')).add_to(m)
    st_folium(m, width="100%", height=550)

# --- REGISTRO ---
with tabs[2]:
    st.header("📸 Registrar Avistamiento")
    with st.form("reg"):
        n = st.text_input("Especie vista")
        isl = st.selectbox("Isla", ["Tenerife", "Gran Canaria", "Lanzarote", "Fuerteventura", "La Palma", "La Gomera", "El Hierro"])
        f = st.file_uploader("Subir foto")
        if st.form_submit_button("Guardar"):
            st.success("¡Registrado con éxito!")




