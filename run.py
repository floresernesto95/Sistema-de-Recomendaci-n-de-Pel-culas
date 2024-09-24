import streamlit as st
import pandas as pd
import requests
import pickle

# Establecer la configuración de la página al principio
st.set_page_config(page_title="Recomendador de Películas", page_icon="", layout="wide")

# Cargar datos de películas preprocesados y matriz de similitud
@st.cache_data
def load_data():
    with open('movie_data.pkl', 'rb') as file:
        movies, cosine_sim = pickle.load(file)
    return movies, cosine_sim

# Función para obtener recomendaciones de películas basadas en similitud
def get_recommendations(title, cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# Función para obtener el póster de la película desde la API de TMDB
@st.cache_data
def fetch_poster(movie_id):
    api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
        return full_path
    return None

# Función para obtener detalles de la película
@st.cache_data
def get_movie_details(movie_id):
    api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    return response.json()

# Función para truncar el título
def truncate_title(title, max_length=17):
    return title[:max_length] + '...' if len(title) > max_length else title

# CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .movie-title {
        font-weight: bold;
        font-size: 1em;
        margin: 0.5rem 0;
        text-align: center;
    }
    .movie-rating {
        font-size: 0.8em;
        color: #FAFAFA;
        text-align: center;
    }
    .selected-movie {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
        background-color: #1e2129;
        padding: 1rem;
        border-radius: 10px;
    }
    .selected-movie-poster {
        width: 200px;
        border-radius: 10px;
    }
    .selected-movie-info {
        flex: 1;
    }
    .stButton>button {
    background-color: #0068c9;
    color: white !important;
    font-size: 16px;
    padding: 10px 20px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    }
    .stButton>button:focus {
    background-color: #0053a3;
    color: white !important;
    box-shadow: none;
    }
    .stButton>button:hover {
        background-color: #0053a3;  /* Tono más oscuro para efecto hover */
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos
movies, cosine_sim = load_data()

st.title("🎬 Sistema de Recomendación de Películas")

# Barra lateral para selección de película
st.sidebar.header("Selecciona una Película")
selected_movie = st.sidebar.selectbox("Elige una película:", movies['title'].values)

# Contenido principal
if selected_movie:
    selected_movie_id = movies[movies['title'] == selected_movie]['movie_id'].values[0]
    poster_url = fetch_poster(selected_movie_id)
    movie_details = get_movie_details(selected_movie_id)
    
    # Mostrar detalles de la película seleccionada
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(poster_url, width=200)
    with col2:
        st.subheader(truncate_title(selected_movie))
        st.write(f"**Fecha de Lanzamiento:** {movie_details.get('release_date', 'N/A')}")
        st.write(f"**Calificación:** {round(movie_details.get('vote_average', 0))}/10")  # Redondeado a entero
        st.write(f"**Duración:** {movie_details.get('runtime', 'N/A')} minutos")
        st.write("**Resumen:**")
        overview = movie_details.get('overview', 'No hay resumen disponible')
        st.write(overview[:250] + '...' if len(overview) > 250 else overview)

    # Obtener y mostrar recomendaciones
    if st.button('Obtener Recomendaciones', key='get_recommendations'):
        recommendations = get_recommendations(selected_movie, cosine_sim)
        st.subheader("Top 10 Películas Recomendadas:")
        
        # Crear un diseño de 5 columnas
        cols = st.columns(5)
        
        for index, (_, row) in enumerate(recommendations.iterrows()):
            movie_title = row['title']
            movie_id = row['movie_id']
            poster_url = fetch_poster(movie_id)
            movie_details = get_movie_details(movie_id)
            
            # Usar módulo para ciclar a través de las columnas
            with cols[index % 5]:
                st.image(poster_url, use_column_width=True)
                st.markdown(f"<p class='movie-title'>{truncate_title(movie_title)}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='movie-rating'>Calificación: {round(movie_details.get('vote_average', 0))}/10</p>", unsafe_allow_html=True)  # Redondeado a entero

# Pie de página
st.sidebar.markdown("---")
st.sidebar.info("Creado por Ernesto")