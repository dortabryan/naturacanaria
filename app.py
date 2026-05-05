import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="NaturaCanaria Pro", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stButton > button {
        border-radius: 15px; height: 100px; width: 100%; background: white;
        color: #2e7d32; border: 2px solid #e8f5e9; font-weight: bold; font-size: 1.1rem;
    }
    .stButton > button:hover { background: #2e7d32; color: white; transform: translateY(-3px); }
    .species-card {
        background: white; border-radius: 15px; overflow: hidden;
        border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .species-card img { width: 100%; height: 200px; object-fit: cover; }
    .card-padding { padding: 15px; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS (Lee el archivo CSV externo)
@st.cache_data
def load_data():
    try:
        return pd.read_csv('especies.csv')
    except:
        # Si no hay CSV, creamos uno básico para que no de error
        return pd.DataFrame([{"Nombre": "Drago", "Cientifico": "Dracaena draco", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.36, "Lon": -16.72, "Desc": "Ejemplo."}])

df = load_data()

# 3. FUNCIÓN DE IMÁGENES REALES (FORZADA)
@st.cache_data
def get_image(scientific_name):
    try:
        # Buscamos en Wikipedia con un agente de usuario para evitar bloqueos
        name = scientific_name.replace(' ', '_')
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{name}"
        r = requests.get(url, headers={'User-Agent': 'NaturaApp/1.0'}, timeout=5).json()
        return r.get('thumbnail', {}).get('source', "https://via.placeholder.com/400?text=Buscando+Foto...")
    except:
        return "https://via.placeholder.com/400?text=No+Disponible"

# 4. INTERFAZ
st.title("🌿 NaturaCanaria Pro")

t_wiki, t_map, t_reg = st.tabs(["🏛️ ENCICLOPEDIA", "🌍 MAPA", "📸 REGISTRO"])

with t_wiki:
    if 'c' not in st.session_state: st.session_state.c = None
    
    st.write("### Elige una categoría:")
    cats = ["Aves", "Marinos", "Anfibios", "Granja", "Reptiles", "Flora"]
    icons = ["🐦", "🐬", "🐸", "🚜", "🦎", "🌸"]
    cols_cat = st.columns(6)
    
    for i, cat in enumerate(cats):
        if cols_cat[i].button(f"{icons[i]}\n{cat}"):
            st.session_state.c = cat

    if st.session_state.c:
        st.divider()
        st.subheader(f"Categoría: {st.session_state.c}")
        sub = df[df['Grupo'] == st.session_state.cat if 'Grupo' in df else df['Grupo'] == st.session_state.c]
        
        grid = st.columns(3)
        for idx, (_, r) in enumerate(sub.iterrows()):
            with grid[idx % 3]:
                foto = get_image(r['Cientifico'])
                st.markdown(f"""
                    <div class="species-card">
                        <img src="{foto}">
                        <div class="card-padding">
                            <h3 style="margin:0; color:#2e7d32;">{r['Nombre']}</h3>
                            <p style="font-style:italic; color:gray; font-size:0.9rem;">{r['Cientifico']}</p>
                            <p><b>📍 {r['Isla']}</b></p>
                            <p style="font-size:0.9rem;">{r['Desc']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with t_map:
    st.subheader("Distribución de especies en las islas")
    m = folium.Map(location=[28.3, -16.0], zoom_start=7)
    for _, r in df.iterrows():
        folium.Marker([r['Lat'], r['Lon']], popup=r['Nombre'], icon=folium.Icon(color='green')).add_to(m)
    st_folium(m, width="100%", height=500)

with t_reg:
    st.header("📸 Registrar Avistamiento")
    with st.form("f"):
        st.text_input("¿Qué has visto?")
        st.selectbox("Isla", ["Tenerife", "GC", "La Palma", "Gomera", "Hierro", "Fuerteventura", "Lanzarote"])
        st.file_uploader("Subir foto")
        if st.form_submit_button("Guardar"):
            st.success("¡Registrado!")
