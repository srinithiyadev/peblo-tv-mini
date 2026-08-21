import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [catalogue, setCatalogue] = useState(null);
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState("");
  const [category, setCategory] = useState("");
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

  if (loading) {
    return <div className="loading">Loading Peblo TV...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  const sections = catalogue?.sections || {};

  const allEpisodes = Object.values(sections).flat();

  const filteredEpisodes = allEpisodes.filter((item) => {
    const matchesSearch =
      !search ||
      item.show_title?.toLowerCase().includes(search.toLowerCase()) ||
      item.title?.toLowerCase().includes(search.toLowerCase()) ||
      item.content_group?.toLowerCase().includes(search.toLowerCase());

    const matchesCategory =
      !category ||
      item.categories?.includes(category);

    const matchesLanguage =
      !language ||
      item.languages?.some(
        (lang) => lang.language === language
      );

    return (
      matchesSearch &&
      matchesCategory &&
      matchesLanguage
    );
  });

  return (
    <div className="viewer">
      <header className="hero">
        <div className="hero-content">
          <h1>Peblo TV</h1>
          <p>Stories, songs and learning for curious kids.</p>
        </div>
      </header>

      <nav className="toolbar">
        <input
          type="text"
          placeholder="Search shows and episodes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

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
          <option value="stories">Stories</option>
          <option value="values">Values</option>
          <option value="folk">Folk</option>
          <option value="songs">Songs</option>
          <option value="learning">Learning</option>
        </select>
      </nav>

      <main>
        {search || language || category ? (
          <section>
            <h2>Search Results</h2>

            <div className="grid">
              {filteredEpisodes.map((item) => (
                <EpisodeCard
                  key={item.content_group}
                  item={item}
                />
              ))}
            </div>

            {filteredEpisodes.length === 0 && (
              <p className="empty">No results found.</p>
            )}
          </section>
        ) : (
          Object.entries(sections).map(
            ([sectionName, entries]) => (
              <section key={sectionName}>
                <div className="section-heading">
                  <h2>
                    {sectionName.charAt(0).toUpperCase() +
                      sectionName.slice(1)}
                  </h2>
                </div>

                <div className="grid">
                  {entries.map((item) => (
                    <EpisodeCard
                      key={item.content_group}
                      item={item}
                    />
                  ))}
                </div>
              </section>
            )
          )
        )}
      </main>

      <footer>
        <p>Peblo TV Catalogue</p>
        <p>
          Generated: {catalogue?.generated_at || "Unknown"}
        </p>
      </footer>
    </div>
  );
}

function EpisodeCard({ item }) {
  const languages =
    item.languages
      ?.map((lang) => lang.language)
      .join(" / ") || "Unknown";

  return (
    <article className="card">
      <div className="card-image">
        {item.artwork?.poster ? (
          <img
            src={`http://127.0.0.1:8000/${item.artwork.poster}`}
            alt={item.title}
          />
        ) : (
          <div className="placeholder">
            Peblo TV
          </div>
        )}
      </div>

      <div className="card-body">
        <h3>{item.title}</h3>

        <p className="show-title">
          {item.show_title}
        </p>

        <p className="meta">
          Episode {item.episode_number}
        </p>

        <p className="meta">
          Languages: {languages}
        </p>

        <div className="tags">
          {item.categories?.map((cat) => (
            <span key={cat}>{cat}</span>
          ))}
        </div>
      </div>
    </article>
  );
}

export default App;