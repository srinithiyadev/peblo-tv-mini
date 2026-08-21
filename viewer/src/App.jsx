import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [episodes, setEpisodes] = useState([]);
  const [search, setSearch] = useState("");
  const [section, setSection] = useState("");
  const [language, setLanguage] = useState("");
  const [status, setStatus] = useState("");
  const [report, setReport] = useState(null);
  const [publishMessage, setPublishMessage] = useState("");
  const [publishRuns, setPublishRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadEpisodes = async () => {
    try {
      setLoading(true);

      const response = await axios.get(`${API}/admin/episodes`);

      const data = response.data;

      setEpisodes(Array.isArray(data) ? data : data.items || []);
    } catch (error) {
      console.error("Failed to load episodes:", error);
      setEpisodes([]);
    } finally {
      setLoading(false);
    }
  };

  const loadValidation = async () => {
    try {
      const response = await axios.get(
        `${API}/admin/validation-report`
      );

      setReport(response.data);
    } catch (error) {
      console.error("Failed to load validation report:", error);
    }
  };

  const loadPublishRuns = async () => {
    try {
      const response = await axios.get(
        `${API}/admin/publish-runs`
      );

      const data = response.data;

      setPublishRuns(
        Array.isArray(data) ? data : data.items || []
      );
    } catch (error) {
      console.error(
        "Failed to load publish history:",
        error
      );

      setPublishRuns([]);
    }
  };

  const publishCatalogue = async () => {
    try {
      setPublishMessage("");

      const response = await axios.post(
        `${API}/admin/publish`
      );

      setPublishMessage(
        `Published successfully: ${response.data.episodes_count} episodes`
      );

      await loadValidation();
      await loadPublishRuns();
    } catch (error) {
      const detail = error.response?.data?.detail;

      if (detail?.issues) {
        setPublishMessage(
          `Publish blocked: ${detail.issues.join(", ")}`
        );
      } else {
        setPublishMessage("Publish failed.");
      }
    }
  };

  useEffect(() => {
    loadEpisodes();
    loadValidation();
    loadPublishRuns();
  }, []);

  const filteredEpisodes = episodes.filter((episode) => {
    const matchesSearch =
      !search ||
      String(episode.episode_id || "")
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      String(episode.title || "")
        .toLowerCase()
        .includes(search.toLowerCase());

    const matchesSection =
      !section || episode.section === section;

    const matchesLanguage =
      !language || episode.language === language;

    const matchesStatus =
      !status || episode.status === status;

    return (
      matchesSearch &&
      matchesSection &&
      matchesLanguage &&
      matchesStatus
    );
  });

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Peblo TV Admin</h1>
          <p>Editorial Content Management</p>
        </div>

        <button
          className="publish-button"
          onClick={publishCatalogue}
        >
          Publish Catalogue
        </button>
      </header>

      {publishMessage && (
        <div className="message">
          {publishMessage}
        </div>
      )}

      <section className="validation-card">
        <div>
          <h2>Validation Report</h2>

          {report ? (
            <p>
              {report.valid
                ? "✓ Catalogue is valid"
                : `⚠ ${report.issue_count} issue(s) found`}
            </p>
          ) : (
            <p>Checking validation...</p>
          )}
        </div>

        {!report?.valid &&
          report?.issues?.length > 0 && (
            <div className="issues">
              {report.issues
                .slice(0, 5)
                .map((issue, index) => (
                  <div key={index}>
                    {issue.message}
                  </div>
                ))}
            </div>
          )}
      </section>

      <section className="history-card">
        <div className="content-header">
          <h2>Publish History</h2>

          <span>
            {publishRuns.length}{" "}
            {publishRuns.length === 1
              ? "run"
              : "runs"}
          </span>
        </div>

        {publishRuns.length === 0 ? (
          <div className="empty">
            No publish runs yet.
          </div>
        ) : (
          <div className="history-list">
            {publishRuns.map((run) => (
              <div
                className="history-item"
                key={run.id}
              >
                <div>
                  <strong>
                    {run.outcome || "Completed"}
                  </strong>

                  <p>
                    {run.started_at
                      ? new Date(
                          run.started_at
                        ).toLocaleString()
                      : "-"}
                  </p>
                </div>

                <div className="history-stats">
                  <span>
                    {run.shows_count ?? 0} shows
                  </span>

                  <span>
                    {run.episodes_count ?? 0} episodes
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="filters">
        <input
          type="text"
          placeholder="Search episode..."
          value={search}
          onChange={(e) =>
            setSearch(e.target.value)
          }
        />

        <select
          value={section}
          onChange={(e) =>
            setSection(e.target.value)
          }
        >
          <option value="">
            All sections
          </option>

          <option value="featured">
            Featured
          </option>

          <option value="series">
            Series
          </option>

          <option value="minisodes">
            Minisodes
          </option>

          <option value="songs">
            Songs
          </option>
        </select>

        <select
          value={language}
          onChange={(e) =>
            setLanguage(e.target.value)
          }
        >
          <option value="">
            All languages
          </option>

          <option value="en">
            English
          </option>

          <option value="hi">
            Hindi
          </option>
        </select>

        <select
          value={status}
          onChange={(e) =>
            setStatus(e.target.value)
          }
        >
          <option value="">
            All statuses
          </option>

          <option value="draft">
            Draft
          </option>

          <option value="published">
            Published
          </option>
        </select>
      </section>

      <section className="content">
        <div className="content-header">
          <h2>Episodes</h2>

          <span>
            {filteredEpisodes.length} episodes
          </span>
        </div>

        {loading ? (
          <div className="empty">
            Loading episodes...
          </div>
        ) : filteredEpisodes.length === 0 ? (
          <div className="empty">
            No episodes found.
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Episode ID</th>
                  <th>Title</th>
                  <th>Language</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Content Group</th>
                </tr>
              </thead>

              <tbody>
                {filteredEpisodes.map(
                  (episode) => (
                    <tr
                      key={
                        episode.id ||
                        episode.episode_id
                      }
                    >
                      <td>
                        {episode.episode_id}
                      </td>

                      <td>
                        {episode.title}
                      </td>

                      <td>
                        <span className="language">
                          {episode.language}
                        </span>
                      </td>

                      <td>
                        <span
                          className={`status ${episode.status}`}
                        >
                          {episode.status}
                        </span>
                      </td>

                      <td>
                        {episode.duration_seconds
                          ? `${episode.duration_seconds}s`
                          : "-"}
                      </td>

                      <td>
                        {episode.content_group}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;