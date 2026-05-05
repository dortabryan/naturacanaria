import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="NaturaCanaria Pro", page_icon="🌿", layout="wide")

# ESTILO CSS MEJORADO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    .stButton > button {
        border-radius: 20px; height: 110px; width: 100%; background: white;
        color: #1b5e20; border: 2px solid #e8f5e9; font-weight: bold; font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .stButton > button:hover { background: #1b5e20; color: white; transform: scale(1.03); }
    
    .species-card {
        background: white; border-radius: 15px; overflow: hidden;
        border: 1px solid #eee; box-shadow: 0 6px 15px rgba(0,0,0,0.1); margin-bottom: 25px;
    }
    .species-card img { width: 100%; height: 230px; object-fit: cover; border-bottom: 2px solid #1b5e20; }
    .card-content { padding: 18px; }
    .status-badge {
        background: #fff3e0; color: #e65100; padding: 3px 10px; border-radius: 10px;
        font-size: 0.75rem; font-weight: bold; text-transform: uppercase;
    }
    .island-badge {
        background: #e8f5e9; color: #2e7d32; padding: 3px 10px; border-radius: 10px;
        font-size: 0.75rem; font-weight: bold; margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        return pd.read_csv('especies.csv')
    except:
        st.error("No se encontró el archivo especies.csv. Por favor, créalo en GitHub.")
        return pd.DataFrame()

df = load_data()

# FUNCIÓN DE FOTOS (WIKIPEDIA)
@st.cache_data
def get_wiki_pic(scientific_name):
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
        r = requests.get(url, timeout=5).json()
        return r.get('thumbnail', {}).get('source', "https://via.placeholder.com/400?text=Sin+Foto")
    except:
        return "https://via.placeholder.com/400?text=Error+Carga"

# NAVEGACIÓN
st.title("🌿 Explorador de Biodiversidad Canaria")
tab_enc, tab_map, tab_reg = st.tabs(["🏛️ ENCICLOPEDIA DETALLADA", "🌍 MAPA DE HÁBITATS", "📸 REGISTRO"])

with tab_enc:
    if 'c' not in st.session_state: st.session_state.c = None
    
    st.write("### Selecciona una categoría para ver detalles técnicos:")
    cats = ["Aves", "Marinos", "Reptiles", "Anfibios", "Granja", "Flora"]
    icons = ["🐦", "🐬", "🦎", "🐸", "🚜", "🌸"]
    c_cols = st.columns(6)
    for i, cat in enumerate(cats):
        if c_cols[i].button(f"{icons[i]}\n{cat}"):
            st.session_state.c = cat

    if st.session_state.c:
        st.divider()
        sub = df[df['Grupo'] == st.session_state.c]
        st.subheader(f"{st.session_state.c} de las Islas ({len(sub)} especies)")
        
        grid = st.columns(3)
        for idx, (_, r) in enumerate(sub.iterrows()):
            with grid[idx % 3]:
                foto = get_wiki_pic(r['Cientifico'])
                st.markdown(f"""
                    <div class="species-card">
                        <img src="{foto}">
                        <div class="card-content">
                            <div style="margin-bottom:10px;">
                                <span class="island-badge">📍 {r['Isla']}</span>
                            </div>
                            <h3 style="margin:0; color:#1b5e20;">{r['Nombre']}</h3>
                            <p style="font-style:italic; color:#666; font-size:0.9rem;">{r['Cientifico']}</p>
                            <p style="font-size:0.95rem; color:#333; line-height:1.4;">{r['Desc']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with tab_map:
    st.subheader("Ubicación representativa de especies")
    if not df.empty:
        m = folium.Map(location=[28.3, -16.0], zoom_start=7)
        for _, r in df.iterrows():
            folium.Marker(
                [r['Lat'], r['Lon']], 
                popup=f"<b>{r['Nombre']}</b><br>{r['Cientifico']}",
                icon=folium.Icon(color='green', icon='leaf')
            ).add_to(m)
        st_folium(m, width="100%", height=550)

with tab_reg:
    st.header("📸 Registro de Avistamiento Personal")
    with st.form("registro"):
        nombre = st.text_input("¿Qué especie has observado?")
        isla = st.selectbox("Isla", ["Tenerife", "Gran Canaria", "Lanzarote", "Fuerteventura", "La Palma", "La Gomera", "El Hierro"])
        nota = st.text_area("Detalles del avistamiento")
        if st.form_submit_button("Guardar Registro"):
            st.success(f"¡{nombre} registrado en {isla}!")
