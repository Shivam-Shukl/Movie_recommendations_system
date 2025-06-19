from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import pickle
import pandas as pd
import os
from datetime import datetime, timedelta
import logging
from functools import lru_cache
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# TMDB API Configuration
TMDB_API_KEY = '32036c19afbb0442c005135fd4fe213f'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
TMDB_BACKDROP_BASE_URL = 'https://image.tmdb.org/t/p/w1280'

# Global variables for recommendation system
similarity = None
movies = None
genres_cache = None

class MovieRecommendationSystem:
    def __init__(self):
        self.load_recommendation_data()
    
    def load_recommendation_data(self):
        """Load the pickle files for recommendation system"""
        try:
            global similarity, movies
            if os.path.exists('similarity.pkl') and os.path.exists('movie_dict.pkl'):
                similarity = pickle.load(open('similarity.pkl', 'rb'))
                movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
                movies = pd.DataFrame(movies_dict)
                logger.info("Recommendation data loaded successfully")
            else:
                logger.warning("Recommendation pickle files not found. Using TMDB recommendations instead.")
                similarity = None
                movies = None
        except Exception as e:
            logger.error(f"Error loading recommendation data: {e}")
            similarity = None
            movies = None

    def get_movie_recommendations(self, movie_title, num_recommendations=5):
        """Get movie recommendations based on similarity"""
        if similarity is None or movies is None:
            return [], []
        
        try:
            # Find the movie index
            movie_matches = movies[movies['title'].str.lower() == movie_title.lower()]
            if movie_matches.empty:
                return [], []
            
            index = movie_matches.index[0]
            distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
            
            recommended_movie_names = []
            recommended_movie_ids = []
            
            for i in distances[1:num_recommendations+1]:
                movie_row = movies.iloc[i[0]]
                recommended_movie_names.append(movie_row.title)
                if 'movie_id' in movie_row:
                    recommended_movie_ids.append(movie_row.movie_id)
                else:
                    recommended_movie_ids.append(None)
            
            return recommended_movie_names, recommended_movie_ids
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return [], []

    def get_all_movies(self):
        """Get all movies from the recommendation dataset"""
        if movies is not None:
            return movies['title'].tolist()
        return []

class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = TMDB_BASE_URL
        self.session = requests.Session()
    
    def _make_request(self, endpoint, params=None):
        """Make API request to TMDB"""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request failed: {e}")
            return None
    
    @lru_cache(maxsize=100)
    def get_movie_details(self, movie_id):
        """Get detailed information about a movie"""
        return self._make_request(f"/movie/{movie_id}")
    
    @lru_cache(maxsize=100)
    def get_movie_credits(self, movie_id):
        """Get movie cast and crew"""
        return self._make_request(f"/movie/{movie_id}/credits")
    
    @lru_cache(maxsize=100)
    def get_similar_movies(self, movie_id):
        """Get similar movies"""
        return self._make_request(f"/movie/{movie_id}/similar")
    
    @lru_cache(maxsize=100)
    def get_movie_videos(self, movie_id):
        """Get movie trailers and videos"""
        return self._make_request(f"/movie/{movie_id}/videos")
    
    def search_movies(self, query, page=1):
        """Search for movies"""
        return self._make_request("/search/movie", {"query": query, "page": page})
    
    def get_trending_movies(self, time_window="week", page=1):
        """Get trending movies"""
        return self._make_request(f"/trending/movie/{time_window}", {"page": page})
    
    def get_popular_movies(self, page=1):
        """Get popular movies"""
        return self._make_request("/movie/popular", {"page": page})
    
    def get_top_rated_movies(self, page=1):
        """Get top rated movies"""
        return self._make_request("/movie/top_rated", {"page": page})
    
    def get_upcoming_movies(self, page=1):
        """Get upcoming movies"""
        return self._make_request("/movie/upcoming", {"page": page})
    
    def get_now_playing_movies(self, page=1):
        """Get now playing movies"""
        return self._make_request("/movie/now_playing", {"page": page})
    
    @lru_cache(maxsize=1)
    def get_genres(self):
        """Get all movie genres"""
        return self._make_request("/genre/movie/list")
    
    def discover_movies(self, **kwargs):
        """Discover movies with filters"""
        return self._make_request("/discover/movie", kwargs)
    
    def get_poster_url(self, poster_path, size="w500"):
        """Get full poster URL"""
        if poster_path:
            return f"https://image.tmdb.org/t/p/{size}{poster_path}"
        return "https://via.placeholder.com/300x450.png?text=No+Poster"
    
    def get_backdrop_url(self, backdrop_path, size="w1280"):
        """Get full backdrop URL"""
        if backdrop_path:
            return f"https://image.tmdb.org/t/p/{size}{backdrop_path}"
        return None

# Initialize components
recommendation_system = MovieRecommendationSystem()
tmdb_client = TMDBClient(TMDB_API_KEY)

# Read the HTML template
# def get_html_content():
#     """Read the HTML content from paste.txt or return inline template"""
#     try:
#         with open('paste.txt', 'r', encoding='utf-8') as f:
#             return f.read()
#     except FileNotFoundError:
#         # Return a basic template if file not found
#         return """
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>CineDiscover - Movie Discovery Platform</title>
#         </head>
#         <body>
#             <h1>CineDiscover</h1>
#             <p>Movie discovery platform is loading...</p>
#             <script>
#                 // Basic API test
#                 fetch('/api/popular')
#                     .then(response => response.json())
#                     .then(data => console.log('API working:', data))
#                     .catch(error => console.error('API error:', error));
#             </script>
#         </body>
#         </html>
#         """

# @app.route('/')
# def index():
#     """Main page - serve the HTML content"""
#     html_content = get_html_content()
#     return render_template_string(html_content)

@app.route('/')
def index():
    """Main page - serve the HTML content from index.html template"""
    return render_template('index.html')

@app.route('/api/trending')
def api_trending():
    """Get trending movies"""
    try:
        data = tmdb_client.get_trending_movies()
        if data and 'results' in data:
            # Add poster URLs
            for movie in data['results']:
                movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            return jsonify(data)
        return jsonify({"results": [], "error": "No data available"})
    except Exception as e:
        logger.error(f"Error fetching trending movies: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/popular')
def api_popular():
    """Get popular movies"""
    try:
        page = request.args.get('page', 1, type=int)
        data = tmdb_client.get_popular_movies(page=page)
        if data and 'results' in data:
            # Add poster URLs
            for movie in data['results']:
                movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            return jsonify(data)
        return jsonify({"results": [], "error": "No data available"})
    except Exception as e:
        logger.error(f"Error fetching popular movies: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search')
def api_search():
    """Search movies"""
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        
        if not query:
            return jsonify({"results": [], "error": "Query is required"})
        
        data = tmdb_client.search_movies(query, page=page)
        if data and 'results' in data:
            # Add poster URLs
            for movie in data['results']:
                movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            return jsonify(data)
        return jsonify({"results": [], "error": "No results found"})
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/movie/<int:movie_id>')
def api_movie_details(movie_id):
    """Get movie details"""
    try:
        movie = tmdb_client.get_movie_details(movie_id)
        credits = tmdb_client.get_movie_credits(movie_id)
        similar = tmdb_client.get_similar_movies(movie_id)
        videos = tmdb_client.get_movie_videos(movie_id)
        
        if movie:
            movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
            movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            
            # Add poster URLs to similar movies
            if similar and 'results' in similar:
                for sim_movie in similar['results']:
                    sim_movie['poster_url'] = tmdb_client.get_poster_url(sim_movie.get('poster_path'))
            
            # Add profile URLs to cast
            if credits and 'cast' in credits:
                for actor in credits['cast']:
                    actor['profile_url'] = tmdb_client.get_poster_url(actor.get('profile_path')) if actor.get('profile_path') else "https://via.placeholder.com/100x100.png?text=No+Photo"
            
            return jsonify({
                'movie': movie,
                'credits': credits,
                'similar': similar,
                'videos': videos
            })
        return jsonify({"error": "Movie not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching movie details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/genres')
def api_genres():
    """Get all genres"""
    try:
        data = tmdb_client.get_genres()
        return jsonify(data if data else {"genres": []})
    except Exception as e:
        logger.error(f"Error fetching genres: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/discover')
def api_discover():
    """Discover movies with filters"""
    try:
        # Get filter parameters
        genre = request.args.get('with_genres')
        year = request.args.get('year')
        sort_by = request.args.get('sort_by', 'popularity.desc')
        min_rating = request.args.get('vote_average.gte')
        page = request.args.get('page', 1, type=int)
        
        # Build parameters
        params = {
            'sort_by': sort_by,
            'page': page
        }
        
        if genre:
            params['with_genres'] = genre
        if year:
            params['year'] = year
        if min_rating:
            params['vote_average.gte'] = min_rating
        
        data = tmdb_client.discover_movies(**params)
        if data and 'results' in data:
            # Add poster URLs
            for movie in data['results']:
                movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            return jsonify(data)
        return jsonify({"results": [], "error": "No data available"})
    except Exception as e:
        logger.error(f"Error discovering movies: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations')
def api_recommendations():
    """Get movie recommendations using the ML model or TMDB fallback"""
    try:
        movie_title = request.args.get('movie', '')
        num_recommendations = request.args.get('count', 5, type=int)
        
        if not movie_title:
            return jsonify({"error": "Movie title is required"}), 400
        
        # Try to get recommendations from our ML model first
        recommended_names, recommended_ids = recommendation_system.get_movie_recommendations(
            movie_title, num_recommendations
        )
        
        recommendations = []
        
        if recommended_names:
            # Use ML model recommendations
            for i, name in enumerate(recommended_names):
                movie_data = {
                    'title': name,
                    'poster_url': "https://via.placeholder.com/300x450.png?text=No+Poster"
                }
                
                # If we have movie ID, get more details from TMDB
                if i < len(recommended_ids) and recommended_ids[i]:
                    details = tmdb_client.get_movie_details(recommended_ids[i])
                    if details:
                        movie_data.update({
                            'id': details.get('id'),
                            'overview': details.get('overview'),
                            'release_date': details.get('release_date'),
                            'vote_average': details.get('vote_average'),
                            'poster_url': tmdb_client.get_poster_url(details.get('poster_path')),
                            'backdrop_url': tmdb_client.get_backdrop_url(details.get('backdrop_path'))
                        })
                
                recommendations.append(movie_data)
        else:
            # Fallback: Search for the movie and get similar movies from TMDB
            search_result = tmdb_client.search_movies(movie_title)
            if search_result and search_result.get('results'):
                first_movie = search_result['results'][0]
                similar_movies = tmdb_client.get_similar_movies(first_movie['id'])
                
                if similar_movies and similar_movies.get('results'):
                    for movie in similar_movies['results'][:num_recommendations]:
                        movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                        movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
                        recommendations.append(movie)
        
        if not recommendations:
            return jsonify({"error": "No recommendations found"}), 404
        
        return jsonify({
            'query': movie_title,
            'recommendations': recommendations
        })
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/list')
def api_movies_list():
    """Get list of all movies in recommendation dataset"""
    try:
        movies_list = recommendation_system.get_all_movies()
        return jsonify({"movies": movies_list})
    except Exception as e:
        logger.error(f"Error fetching movies list: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-rated')
def api_top_rated():
    """Get top rated movies"""
    try:
        page = request.args.get('page', 1, type=int)
        data = tmdb_client.get_top_rated_movies(page=page)
        if data and 'results' in data:
            # Add poster URLs
            for movie in data['results']:
                movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            return jsonify(data)
        return jsonify({"results": [], "error": "No data available"})
    except Exception as e:
        logger.error(f"Error fetching top rated movies: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upcoming')
def api_upcoming():
    """Get upcoming movies"""
    try:
        page = request.args.get('page', 1, type=int)
        data = tmdb_client.get_upcoming_movies(page=page)
        if data and 'results' in data:
            # Add poster URLs
            for movie in data['results']:
                movie['poster_url'] = tmdb_client.get_poster_url(movie.get('poster_path'))
                movie['backdrop_url'] = tmdb_client.get_backdrop_url(movie.get('backdrop_path'))
            return jsonify(data)
        return jsonify({"results": [], "error": "No data available"})
    except Exception as e:
        logger.error(f"Error fetching upcoming movies: {e}")
        return jsonify({"error": str(e)}), 500

# Additional routes for better compatibility
@app.route('/recommendations')
def recommendations_page():
    """Recommendations page - same as main page"""
    return index()

@app.route('/movie/<int:movie_id>')
def movie_details_page(movie_id):
    """Individual movie details page - same as main page"""
    return index()

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# CORS headers for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css')
        os.makedirs('static/js')
        os.makedirs('static/images')
    
    # Check if required files exist
    required_files = ['similarity.pkl', 'movie_dict.pkl']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        logger.warning(f"Missing recommendation files: {missing_files}")
        logger.warning("Recommendation system will use TMDB fallback instead.")
    
    print("Starting CineDiscover Movie Platform...")
    print("Available at: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("- GET /api/trending - Get trending movies")
    print("- GET /api/popular - Get popular movies")
    print("- GET /api/search?q=query - Search movies")
    print("- GET /api/movie/{id} - Get movie details")
    print("- GET /api/recommendations?movie=title - Get recommendations")
    print("- GET /api/genres - Get all genres")
    print("- GET /api/discover - Discover movies with filters")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)