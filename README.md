# CineDiscover - Movie Discovery Platform

CineDiscover is a modern web-based movie discovery platform that allows users to explore trending and popular movies, search for specific films, view detailed information (including cast and similar movies), and get AI-powered recommendations based on their favorite titles.

## Features

### 1. **Hero Section & Navigation**
- **Hero Section:** Eye-catching, animated hero area with a carousel of popular movies as dynamic background images.
- **Navigation Bar:** Fixed, responsive navigation bar with links to Trending, Popular, and Recommendations sections. Highlights when the user scrolls.

### 2. **Trending Movies**
- **Section:** Displays a grid of trending movies fetched from the backend API.
- **Movie Cards:** Shows movie poster, title, rating, and genres.
- **Loading Spinner:** Animated loading indicator while fetching data.

### 3. **Popular Movies**
- **Section:** Shows a grid of currently popular movies, similar to the Trending section.
- **Card Hover Effect:** Subtle animation and shadow on hover for better UX.

### 4. **Movie Search**
- **Live Search:** Users can search for movies by title using the search bar in the hero section.
- **Debounced Input:** Input is debounced for performance, and search is triggered after a short pause in typing.
- **Search Results Section:** Displays search results in a responsive grid.

### 5. **Movie Details Modal**
- **Detailed View:** Clicking a movie card opens a modal with:
  - Large backdrop image
  - Poster, title, rating, release year, and genres
  - Overview/description
  - Cast members (with photos and names)
  - Similar movies (displayed as cards)
- **Modal Controls:** ESC key and click-outside both close the modal.

### 6. **AI Movie Recommendations**
- **Input:** Users enter a movie they like to get recommendations.
- **Recommendation Results:** AI suggests similar movies, rendered as a grid of cards.
- **Loading State:** Spinner while recommendations are fetched.
- **Error Handling:** User-friendly error messages for invalid queries.

### 7. **Responsive & Modern UI**
- **Mobile-friendly:** Layout adapts for smaller screens.
- **Modern Aesthetics:** Uses gradients, blur effects, and animated elements for a cinematic feel.
- **Accessibility:** Keyboard shortcuts and clear focus styles.

### 8. **Other UI/UX Features**
- **Smooth Scrolling:** Navigation links smoothly scroll to their respective sections.
- **Error Handling:** Displays error messages when API calls fail.
- **Performance:** Uses `loading="lazy"` for images and debounces inputs.

---

## API Endpoints Used

- `/api/genres` - Fetches list of movie genres.
- `/api/trending` - Fetches trending movies.
- `/api/popular` - Fetches popular movies.
- `/api/search?q=...` - Searches for movies by a query string.
- `/api/movie/:id` - Fetches detailed information, credits, and similar movies for a given movie ID.
- `/api/recommendations?movie=...` - Fetches AI-powered movie recommendations based on a title.

---

## Getting Started

> **Note:** The frontend expects a compatible backend serving the above API endpoints.

1. **Clone the repository**
2. **Set up the backend API** (make sure it supports the required endpoints)
3. **Open the `index.html` file in your browser** (or serve with a local web server for best results)

---

## Customization

- **Styling:** All styles are defined in the `<style>` section of the HTML; you can easily customize colors, fonts, and effects.
- **API Base URL:** The frontend uses `window.location.origin + '/api'` as the base URL for API calls. Adjust as needed for your backend setup.

---

## Credits

- Movie data is expected to be fetched from a backend that may use TMDB or similar APIs.
- UI inspiration from modern streaming and discovery platforms.

---

## License

MIT License
