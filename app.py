import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="NaturaCanaria Pro", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .species-card {
        background: white; padding: 15px; border-radius: 15px;
        border: 1px solid #ddd; margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .species-card img {
        width: 100%; height: 200px; border-radius: 10px; object-fit: cover;
        background-color: #eee;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9; border-radius: 10px; padding: 10px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('especies.csv')
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame([
            {"Nombre": "Pinzón Azul", "Cientifico": "Fringilla teydea", "Grupo": "Aves", "Isla": "Tenerife", "Lat": 28.27, "Lon": -16.64, "Desc": "Pinares de Tenerife."},
            {"Nombre": "Tajinaste Rojo", "Cientifico": "Echium wildpretii", "Grupo": "Flora", "Isla": "Tenerife", "Lat": 28.21, "Lon": -16.62, "Desc": "Cumbres del Teide."}
        ])

df = load_data()

# 3. FUNCIÓN DE FOTOS MEJORADA (Búsqueda más agresiva)
@st.cache_data
def get_wiki_image(scientific_name):
    name = scientific_name.replace(' ', '_')
    try:
        # Intentamos obtener la imagen principal de la Wikipedia en español
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{name}"
        headers = {'User-Agent': 'NaturaCanariaApp/1.0 (contacto@tuemail.com)'}
        res = requests.get(url, headers=headers, timeout=5).json()
        if 'thumbnail' in res:
            return res['thumbnail']['source']
        
        # Si falla, intentamos en la Wikipedia en Inglés (suele tener más fotos científicas)
        url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
        res_en = requests.get(url_en, headers=headers, timeout=5).json()
        if 'thumbnail' in res_en:
            return res_en['thumbnail']['source']
    except:
        pass
    return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

# 4. INTERFAZ
st.title("🌿 NaturaCanaria Pro")

tab1, tab2, tab3 = st.tabs(["📚 CATEGORÍAS", "📍 MAPA REAL", "📸 REGISTRAR AVISTAMIENTO"])

with tab1:
    search = st.text_input("🔍 Buscar en la enciclopedia...")
    display_df = df if not search else df[df['Nombre'].str.contains(search, case=False)]
    
    grupos = display_df['Grupo'].unique()
    for grupo in grupos:
        with st.expander(f"📁 {grupo.upper()}", expanded=True):
            sub_df = display_df[display_df['Grupo'] == grupo]
            cols = st.columns(3)
            for i, (_, row) in enumerate(sub_df.iterrows()):
                with cols[i % 3]:
                    foto = get_wiki_image(row['Cientifico'])
                    st.markdown(f"""
                        <div class="species-card">
                            <img src="{foto}">
                            <h3 style="color:#2e7d32; margin:10px 0 5px 0;">{row['Nombre']}</h3>
                            <p><i>{row['Cientifico']}</i></p>
                            <p><b>Isla:</b> {row['Isla']}</p>
                            <p style="font-size:0.9em;">{row['Desc']}</p>
                        </div>
                    """, unsafe_allow_html=True)

with tab2:
    st.subheader("Mapa de Ubicaciones en Tierra")
    m = folium.Map(location=[28.3, -15.8], zoom_start=7)
    for _, row in df.iterrows():
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=row['Nombre'],
            tooltip=row['Nombre'],
            icon=folium.Icon(color='green', icon='leaf')
        ).add_to(m)
    st_folium(m, width="100%", height=500)

with tab3:
    st.header("📸 Nuevo Registro")
    st.write("Registra lo que has visto en tu última excursión.")
    with st.form("form_registro"):
        nombre_obs = st.text_input("¿Qué has visto?")
        isla_obs = st.selectbox("¿En qué isla?", ["Tenerife", "Gran Canaria", "La Palma", "La Gomera", "El Hierro", "Fuerteventura", "Lanzarote"])
        foto_subida = st.file_uploader("Sube tu propia foto", type=['jpg', 'png', 'jpeg'])
        detalles = st.text_area("Notas adicionales (lugar exacto, comportamiento...)")
        
        if st.form_submit_button("Guardar en mi diario"):
            if nombre_obs:
                st.success(f"✅ ¡Avistamiento de {nombre_obs} registrado correctamente!")
                if foto_subida:
                    st.image(foto_subida, caption="Tu foto registrada")
            else:
                st.error("Por favor, introduce al menos el nombre de la especie.")

