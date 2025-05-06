import streamlit as st
import requests
import re
import json
import base64
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_KEY = os.getenv("API_KEY")
st.set_page_config(
    page_title="Intelligent Movie Recommender \U0001F3AC",
    page_icon="\U0001F3AC",
    layout="centered",
    initial_sidebar_state="auto",
)

# Encode uploaded banner image
with open("wallpaperflare.com_wallpaper.jpg", "rb") as img_file:
    encoded_banner = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #1c1f26;
        color: white;
        overflow-x: hidden;
    }}
    .header-banner {{
        width: 100%;
        height: 250px;
        background-image: url('data:image/jpg;base64,{encoded_banner}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-bottom: 3px solid #800000;
    }}
    .block-container {{
        padding-top: 0px;
        max-width: 1050px;
    }}
    .stTextInput>div>div>input,
    .stTextArea textarea {{
        background-color: white;
        color: black;
        border: 2px solid #c00000;
        border-radius: 6px;
        font-size: 14px;
        padding: 6px;
    }}
    .stSlider > div > div > div > div {{
        background: transparent !important;
        height: 20px !important;
        position: relative;
    }}
    .stSlider > div > div > div > div::before {{
        content: "";
        position: absolute;
        top: 50%;
        left: 0;
        height: 3px;
        width: 100%;
        background-color: #ff3333;
        transform: translateY(-50%);
        z-index: 2;
    }}
    .stSlider .css-14xtw13 {{
        background-color: transparent !important;
    }}
    .stSlider label {{
        margin-bottom: 4px !important;
        color: white;
    }}
    .stSlider span {{
        color: white !important;
    }}
    .stButton button {{
        background-color: #800000;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: 15px;
    }}
    .stButton button:hover {{
        background-color: #a00000;
    }}
    .element-container:has(.stImage) {{
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 1.5rem;
        margin-top: 1.5rem;
        padding: 1rem;
        background-color: #1b1b1b;
        border: 1px solid #800000;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(128, 0, 0, 0.5);
    }}
    label, .stTextInput label, .stTextArea label {{
        color: white !important;
    }}
    .stSelectbox>div>div>div>div {{
        all: unset !important;
    }}
    .stDeployButton {{
        filter: brightness(180%) contrast(130%);
    }}
    .side-accent-left, .side-accent-right {{
        position: fixed;
        top: 0;
        height: 100%;
        width: 150px;
        background: linear-gradient(to bottom, #800000, transparent);
        z-index: 1;
    }}
    .side-accent-left {{ left: 0; }}
    .side-accent-right {{ right: 0; }}
    header[data-testid="stHeader"] {{
        background-color: #800000 !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
    }}
    </style>
    <div class="header-banner"></div>
    <div class="side-accent-left"></div>
    <div class="side-accent-right"></div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<h1 style='font-size: 48px;'>🎬 Intelligent Movie Recommender</h1>
<h4 style='color: white;'>Find movies based on your mood, keywords in reviews, genres, and more!</h4>
""", unsafe_allow_html=True)

# UI inputs
sort_option = st.selectbox("Sort movies by:", ["Popularity", "Rating", "Release Date"])
min_rating_input = st.slider("Minimum Rating (0-10):", 0.0, 10.0, 0.0, 0.1)
year_cat = st.selectbox("Select Year Category:", ["Any", "2020", "2010", "2000", "1990", "1980", "1970"])
genre_input = st.text_input("Enter Genre (optional):")
actor_input = st.text_input("Enter Actor Name (optional):")
director_input = st.text_input("Enter Director Name (optional):")
description_input = st.text_area("Description of the movie you want to find:")
country_name_input = st.text_input("Enter Country Name (optional, e.g., United States, France, Japan):")
language_name_input = st.text_input("Enter Language Name (optional, e.g., English, French, Japanese):")

def get_country_code(name):
    response = requests.get("https://api.themoviedb.org/3/configuration/countries", params={'api_key': API_KEY})
    if response.status_code == 200:
        for c in response.json():
            if name.lower() in c['english_name'].lower():
                return c['iso_3166_1']
    return None

def get_language_code(name):
    response = requests.get("https://api.themoviedb.org/3/configuration/languages", params={'api_key': API_KEY})
    if response.status_code == 200:
        for l in response.json():
            if name.lower() in l['english_name'].lower():
                return l['iso_639_1']
    return None

def fetch_reviews(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    params = {'api_key': API_KEY}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json().get('results', [])
    return []

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    r = requests.get(url, params={'api_key': API_KEY})
    if r.status_code == 200:
        return r.json()
    return None

def discover_movies():
    url = "https://api.themoviedb.org/3/discover/movie"
    sort_by = {
        "Popularity": "popularity.desc",
        "Rating": "vote_average.desc",
        "Release Date": "primary_release_date.desc"
    }[sort_option]

    params = {
        'api_key': API_KEY,
        'sort_by': sort_by,
        'vote_average.gte': min_rating_input
    }

    if year_cat != "Any":
        params['primary_release_year'] = year_cat

    if country_name_input:
        code = get_country_code(country_name_input)
        if code:
            params['with_origin_country'] = code

    if language_name_input:
        code = get_language_code(language_name_input)
        if code:
            params['with_original_language'] = code

    if genre_input:
        genre_search = requests.get("https://api.themoviedb.org/3/genre/movie/list", params={'api_key': API_KEY})
        if genre_search.status_code == 200:
            genres = genre_search.json()['genres']
            genre_id = next((g['id'] for g in genres if genre_input.lower() in g['name'].lower()), None)
            if genre_id:
                params['with_genres'] = genre_id

    if actor_input:
        res = requests.get("https://api.themoviedb.org/3/search/person", params={'api_key': API_KEY, 'query': actor_input})
        if res.status_code == 200 and res.json()['results']:
            params['with_cast'] = res.json()['results'][0]['id']

    if director_input:
        res = requests.get("https://api.themoviedb.org/3/search/person", params={'api_key': API_KEY, 'query': director_input})
        if res.status_code == 200 and res.json()['results']:
            params['with_crew'] = res.json()['results'][0]['id']

    response = requests.get(url, params={k: v for k, v in params.items() if v})
    if response.status_code == 200:
        return response.json()['results']
    return []

def find_multiple_titles_with_gemini(user_description, actor=None):
    if actor:
        user_description += f" (preferably with {actor} in cast)"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f'A user described a movie as: "{user_description}".\n'
                            f'Based on your knowledge of cinema, suggest up to 3 movie titles that best match this description.\n'
                            f'Respond with one title per line, each in double quotes, e.g.:\n'
                            f'"Inception"\n"Interstellar"\n"The Prestige"\n'
                            f'Do NOT write anything else.'
                        )
                    }
                ]
            }
        ]
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(data))
        if r.status_code == 200:
            content = r.json()['candidates'][0]['content']['parts'][0]['text']
            titles = re.findall(r'"([^\"]+)"', content)
            return titles
        else:
            print(f"Gemini API error: {r.text}")
            return []
    except Exception as e:
        print(f"Gemini exception: {e}")
        return []

if st.button("\U0001F50D Recommend"):
    use_ai = bool(description_input.strip())

    if use_ai:
        st.info("\U0001F9E0 Asking Gemini to suggest matching movies based on your description...")
        titles = find_multiple_titles_with_gemini(description_input, actor=actor_input)

        if not titles:
            st.error("❌ Gemini could not suggest any titles.")
        else:
            st.success(f"✅ Gemini suggests: {', '.join(titles)}")

            for title in titles:
                search_url = "https://api.themoviedb.org/3/search/movie"
                params = {"api_key": API_KEY, "query": title}
                response = requests.get(search_url, params=params)
                results = response.json().get("results", [])
                if results:
                    movie = results[0]
                    st.markdown("---")
                    tmdb_url = f"https://www.themoviedb.org/movie/{movie['id']}"
                    st.markdown(f"\U0001F3AC [**{movie['title']}**]({tmdb_url}) ({movie.get('release_date', 'Unknown')[:4]})")

                    # Set layout with image and text side by side
                    col1, col2 = st.columns([1, 3])  # 1 part for the image, 3 parts for the text

                    with col1:
                        if movie.get('poster_path'):
                            st.image(f"https://image.tmdb.org/t/p/w200{movie['poster_path']}", width=150)
                    with col2:
                        # Display movie rating
                        st.markdown(f"*Rating:* {movie.get('vote_average', 'N/A')}/10")
                        
                        # Display movie overview
                        st.markdown(f"*Overview:* {movie.get('overview', 'No description available.')}")

                        # Fetch the credits (cast and crew)
                        credits = fetch_movie_details(movie['id'])
                        if credits:
                            cast = credits.get('cast', [])[:5]
                            crew = credits.get('crew', [])
                            directors = [m['name'] for m in crew if m['job'] == 'Director']
                            
                            # Display the actors
                            if cast:
                                st.markdown(f"*Actors:* {', '.join(actor['name'] for actor in cast)}")
                            
                            # Display the directors
                            if directors:
                                st.markdown(f"*Director:* {', '.join(directors)}")
                    
                        # Display genres
                        genres_url = f"https://api.themoviedb.org/3/movie/{movie['id']}"
                        genres_resp = requests.get(genres_url, params={'api_key': API_KEY})
                        if genres_resp.status_code == 200:
                            genres_data = genres_resp.json()
                            if 'genres' in genres_data:
                                genre_names = ', '.join(g['name'] for g in genres_data['genres'])
                                st.markdown(f"*Genres:* {genre_names}")
    else:
        # Code for regular movie search
        movies = discover_movies()

        if not movies:
            st.warning("No matching movies found.")
        else:
            st.success(f"✅ Found {len(movies)} movies.")

            for movie in movies:
                credits = fetch_movie_details(movie['id'])

                st.markdown("---")
                tmdb_url = f"https://www.themoviedb.org/movie/{movie['id']}"
                st.markdown(f"\U0001F3AC [**{movie['title']}**]({tmdb_url}) ({movie.get('release_date', 'Unknown')[:4]})")
                
                # Set layout with image and text side by side
                col1, col2 = st.columns([1, 3])  # 1 part for the image, 3 parts for the text

                with col1:
                    if movie.get('poster_path'):
                        st.image(f"https://image.tmdb.org/t/p/w200{movie['poster_path']}", width=150)

                with col2:
                    st.markdown(f"*Rating:* {movie.get('vote_average', 'N/A')}/10")
                    st.markdown(f"*Overview:* {movie.get('overview', 'No description available.')}")

                    # Display credits (actors and directors)
                    if credits:
                        cast = credits.get('cast', [])[:5]
                        crew = credits.get('crew', [])
                        directors = [m['name'] for m in crew if m['job'] == 'Director']
                        if cast:
                            st.markdown(f"*Actors:* {', '.join(actor['name'] for actor in cast)}")
                        if directors:
                            st.markdown(f"*Director:* {', '.join(directors)}")

                    # Display genres
                    genres_url = f"https://api.themoviedb.org/3/movie/{movie['id']}"
                    genres_resp = requests.get(genres_url, params={'api_key': API_KEY})
                    if genres_resp.status_code == 200:
                        genres_data = genres_resp.json()
                        if 'genres' in genres_data:
                            genre_names = ', '.join(g['name'] for g in genres_data['genres'])
                            st.markdown(f"*Genres:* {genre_names}")
