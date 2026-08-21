import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [episodes, setEpisodes] = useState([]);
  const [search, setSearch] = useState("");
  const [section, setSection] = useState("");
  const [language, setLanguage] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadEpisodes = async () => {
      try {
        setLoading(true);
        setError("");

        /*
         * The admin API contains the complete episode catalogue.
         * Viewer shows published episodes only and ignores trailers.
         */
        const response = await axios.get(
          `${API}/admin/episodes`
        );

        const data = response.data;

        const items = Array.isArray(data)
          ? data
          : data.items || [];

        const publishedEpisodes = items.filter(
          (episode) =>
            episode.status === "published" &&
            !String(
              episode.content_group || ""
            ).includes("-s00")
        );

        setEpisodes(publishedEpisodes);
      } catch (err) {
        console.error(
          "Failed to load episodes:",
          err
        );

        setError("Unable to load Peblo TV catalogue.");
      } finally {
        setLoading(false);
      }
    };

    loadEpisodes();
  }, []);

  const filteredEpisodes = useMemo(() => {
    const query = search.trim().toLowerCase();

    return episodes.filter((episode) => {
      const matchesSearch =
        !query ||
        String(episode.title || "")
          .toLowerCase()
          .includes(query) ||
        String(episode.content_group || "")
          .toLowerCase()
          .includes(query);

      const matchesSection =
        !section ||
        episode.section === section;

      const matchesLanguage =
        !language ||
        episode.language === language;

      const matchesCategory =
        !category ||
        (
          Array.isArray(episode.categories)
            ? episode.categories
            : []
        ).includes(category);

      return (
        matchesSearch &&
        matchesSection &&
        matchesLanguage &&
        matchesCategory
      );
    });
  }, [
    episodes,
    search,
    section,
    language,
    category,
  ]);

  const getShowName = (contentGroup) => {
    if (!contentGroup) {
      return "Peblo TV";
    }

    const value = String(contentGroup);

    const parts = value.split("-s01e");

    if (parts[0]) {
      return parts[0]
        .split("-")
        .map(
          (word) =>
            word.charAt(0).toUpperCase() +
            word.slice(1)
        )
        .join(" ");
    }

    return "Peblo TV";
  };

  const getPoster = (episode) => {
    return (
      episode.poster ||
      episode.thumbnail ||
      episode.artwork?.poster ||
      episode.artwork?.thumbnail ||
      episode.image ||
      episode.image_url ||
      ""
    );
  };

  const formatDuration = (seconds) => {
    if (!seconds) {
      return "-";
    }

    const minutes = Math.floor(seconds / 60);
    const remaining = seconds % 60;

    return `${minutes}:${String(
      remaining
    ).padStart(2, "0")}`;
  };

  const languageName = (languageCode) => {
    if (languageCode === "en") {
      return "English";
    }

    if (languageCode === "hi") {
      return "Hindi";
    }

    return languageCode || "Unknown";
  };

  const getCategories = (episode) => {
    if (Array.isArray(episode.categories)) {
      return episode.categories;
    }

    if (Array.isArray(episode.tags)) {
      return episode.tags;
    }

    return ["adventure", "india", "friendship"];
  };

  return (
    <div className="viewer-app">
      <header className="viewer-header">
        <div className="brand">
          <h1>Peblo TV</h1>
          <p>
            Stories, songs and learning for curious kids.
          </p>
        </div>
      </header>

      <main className="viewer-content">
        <section className="hero">
          <div>
            <h2>Peblo TV</h2>
            <p>
              Stories, songs and learning for curious kids.
            </p>
          </div>
        </section>

        <section className="viewer-controls">
          <input
            type="text"
            placeholder="Search shows, episodes or categories..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

          <select
            value={section}
            onChange={(event) =>
              setSection(event.target.value)
            }
          >
            <option value="">All sections</option>
            <option value="featured">Featured</option>
            <option value="series">Series</option>
            <option value="minisodes">
              Minisodes
            </option>
            <option value="songs">Songs</option>
          </select>

          <select
            value={language}
            onChange={(event) =>
              setLanguage(event.target.value)
            }
          >
            <option value="">All languages</option>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </select>

          <select
            value={category}
            onChange={(event) =>
              setCategory(event.target.value)
            }
          >
            <option value="">All categories</option>
            <option value="adventure">
              Adventure
            </option>
            <option value="india">India</option>
            <option value="friendship">
              Friendship
            </option>
          </select>
        </section>

        {loading && (
          <div className="viewer-message">
            Loading catalogue...
          </div>
        )}

        {!loading && error && (
          <div className="viewer-message error">
            {error}
          </div>
        )}

        {!loading &&
          !error &&
          filteredEpisodes.length === 0 && (
            <div className="viewer-message">
              No episodes found.
            </div>
          )}

        {!loading &&
          !error &&
          filteredEpisodes.length > 0 && (
            <section className="catalogue">
              <div className="catalogue-heading">
                <h2>Explore Peblo TV</h2>

                <span>
                  {filteredEpisodes.length} episodes
                </span>
              </div>

              <div className="episode-grid">
                {filteredEpisodes.map(
                  (episode, index) => {
                    const poster = getPoster(episode);
                    const categories =
                      getCategories(episode);

                    return (
                      <article
                        className="episode-card"
                        key={
                          episode.id ||
                          episode.episode_id ||
                          `${episode.content_group}-${index}`
                        }
                      >
                        <div className="poster">
                          {poster ? (
                            <img
                              src={poster}
                              alt={episode.title}
                            />
                          ) : (
                            <div className="poster-placeholder">
                              Peblo TV
                            </div>
                          )}
                        </div>

                        <div className="episode-info">
                          <div className="section-label">
                            {episode.section ||
                              "Featured"}
                          </div>

                          <h3>
                            {episode.title ||
                              "Untitled Episode"}
                          </h3>

                          <div className="show-name">
                            {getShowName(
                              episode.content_group
                            )}
                          </div>

                          <div className="episode-meta">
                            <span>
                              Episode{" "}
                              {episode.episode_number ||
                                ""}
                            </span>

                            <span>
                              {formatDuration(
                                episode.duration_seconds
                              )}
                            </span>

                            <span>
                              {languageName(
                                episode.language
                              )}
                            </span>
                          </div>

                          <div className="tags">
                            {categories
                              .slice(0, 3)
                              .map((tag) => (
                                <span
                                  key={tag}
                                  className="tag"
                                >
                                  {tag}
                                </span>
                              ))}
                          </div>
                        </div>
                      </article>
                    );
                  }
                )}
              </div>
            </section>
          )}
      </main>
    </div>
  );
}

export default App;