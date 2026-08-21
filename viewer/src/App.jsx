import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [catalogue, setCatalogue] = useState(null);
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState("");
  const [category, setCategory] = useState("");
  const [section, setSection] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get(`${API}/catalog`)
      .then((response) => {
        setCatalogue(response.data);
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to load catalogue.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const episodes = catalogue?.episodes || [];

  const sections = useMemo(() => {
    return [...new Set(
      episodes
        .map((episode) => episode.section)
        .filter(Boolean)
    )];
  }, [episodes]);

  const categories = useMemo(() => {
    return [...new Set(
      episodes.flatMap(
        (episode) => episode.categories || []
      )
    )].sort();
  }, [episodes]);

  const filteredEpisodes = useMemo(() => {
    return episodes.filter((episode) => {
      const searchText = search.trim().toLowerCase();

      const matchesSearch =
        !searchText ||
        episode.show_title?.toLowerCase().includes(searchText) ||
        episode.title?.toLowerCase().includes(searchText) ||
        episode.content_group?.toLowerCase().includes(searchText) ||
        episode.categories?.some((cat) =>
          cat.toLowerCase().includes(searchText)
        );

      const matchesLanguage =
        !language ||
        episode.language === language;

      const matchesCategory =
        !category ||
        episode.categories?.includes(category);

      const matchesSection =
        !section ||
        episode.section === section;

      return (
        matchesSearch &&
        matchesLanguage &&
        matchesCategory &&
        matchesSection
      );
    });
  }, [
    episodes,
    search,
    language,
    category,
    section,
  ]);

  if (loading) {
    return (
      <div className="loading">
        Loading Peblo TV...
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        {error}
      </div>
    );
  }

  return (
    <div className="viewer">
      <header className="hero">
        <div className="hero-content">
          <h1>Peblo TV</h1>
          <p>
            Stories, songs and learning for curious kids.
          </p>
        </div>
      </header>

      <div className="toolbar">
        <input
          type="text"
          placeholder="Search shows, episodes or categories..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={section}
          onChange={(e) => setSection(e.target.value)}
        >
          <option value="">All sections</option>

          {sections.map((item) => (
            <option key={item} value={item}>
              {formatLabel(item)}
            </option>
          ))}
        </select>

        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="">All languages</option>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
        </select>

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">All categories</option>

          {categories.map((item) => (
            <option key={item} value={item}>
              {formatLabel(item)}
            </option>
          ))}
        </select>
      </div>

      <main>
        <div className="results-header">
          <h2>
            {search || language || category || section
              ? "Search Results"
              : "Explore Peblo TV"}
          </h2>

          <span>
            {filteredEpisodes.length} episodes
          </span>
        </div>

        {filteredEpisodes.length === 0 ? (
          <div className="empty">
            <h3>No episodes found</h3>
            <p>
              Try changing your search or filters.
            </p>
          </div>
        ) : (
          <div className="grid">
            {filteredEpisodes.map((episode) => (
              <EpisodeCard
                key={episode.episode_id}
                episode={episode}
              />
            ))}
          </div>
        )}
      </main>

      <footer>
        <span>Peblo TV Catalogue</span>

        <span>
          Generated:{" "}
          {catalogue?.generated_at || "Unknown"}
        </span>
      </footer>
    </div>
  );
}


function EpisodeCard({ episode }) {
  const poster =
  episode.artwork?.poster ||
  "/uploads/default-poster.jpg";

const imageUrl = `${API}${poster}`;  

  return (
    <article className="card">
      <div className="card-image">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={episode.title}
            onError={(event) => {
              event.currentTarget.style.display = "none";
            }}
          />
        ) : (
          <div className="placeholder">
            <span>Peblo TV</span>
          </div>
        )}
      </div>

      <div className="card-body">
        <div className="section-label">
          {formatLabel(episode.section)}
        </div>

        <h3>{episode.title}</h3>

        <p className="show-title">
          {episode.show_title}
        </p>

        <div className="meta-row">
          <span>
            Episode {episode.episode_number}
          </span>

          <span>
            {formatDuration(episode.duration_seconds)}
          </span>

          <span>
            {episode.language?.toUpperCase()}
          </span>
        </div>

        <div className="tags">
          {(episode.categories || []).map((category) => (
            <span key={category}>
              {category}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}


function formatLabel(value) {
  if (!value) {
    return "";
  }

  return value
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}


function formatDuration(seconds) {
  if (!seconds) {
    return "0m";
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (remainingSeconds === 0) {
    return `${minutes}m`;
  }

  return `${minutes}m ${remainingSeconds}s`;
}


export default App;
