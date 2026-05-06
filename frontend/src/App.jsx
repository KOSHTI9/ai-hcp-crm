import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [message, setMessage] = useState(
    "Met Dr. Smith today. Discussed Product X efficacy. Sentiment was positive. Shared brochure."
  );
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);

  const sendMessage = async () => {
    try {
      setLoading(true);
      const res = await axios.post("http://127.0.0.1:8000/agent/chat", {
        message,
      });
      setAiResult(res.data);
    } catch (error) {
      alert("Error calling AI agent");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const saved = aiResult?.saved_interaction;

  return (
    <div className="page">
      <header className="header">
        <h1>AI-HCP CRM</h1>
        <p>Log HCP interactions using structured fields or AI chat.</p>
      </header>

      <main className="layout">
        <section className="card">
          <h2>Conversational Logging</h2>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe your HCP interaction..."
          />
          <button onClick={sendMessage} disabled={loading}>
            {loading ? "Processing..." : "Ask AI to Log Interaction"}
          </button>

          {aiResult && (
            <div className="tools">
              <h3>LangGraph Tools Used</h3>
              <p>✅ Search HCP: {aiResult.tool_1_search_hcp}</p>
              <p>✅ Log Interaction ID: {aiResult.tool_2_log_interaction}</p>
              <p>✅ Edit Interaction: {aiResult.tool_3_edit_interaction}</p>
              <p>✅ Summary Generated</p>
              <p>✅ Follow-up Recommended</p>
            </div>
          )}
        </section>

        <section className="card">
          <h2>Structured Log Interaction Form</h2>

          <label>HCP ID</label>
          <input value={saved?.hcp_id || ""} readOnly />

          <label>Interaction Type</label>
          <input value="Meeting" readOnly />

          <label>Topics Discussed</label>
          <input value={saved?.topics_discussed || ""} readOnly />

          <label>Materials Shared</label>
          <input value={saved?.materials_shared || ""} readOnly />

          <label>Sentiment</label>
          <div className="sentiment">
            <span className={saved?.sentiment === "Positive" ? "active" : ""}>
              Positive
            </span>
            <span className={saved?.sentiment === "Neutral" ? "active" : ""}>
              Neutral
            </span>
            <span className={saved?.sentiment === "Negative" ? "active" : ""}>
              Negative
            </span>
          </div>

          <label>AI Summary</label>
          <textarea value={aiResult?.tool_4_summary || ""} readOnly />

          <label>Follow-up Actions</label>
          <textarea value={saved?.follow_up_actions || ""} readOnly />
        </section>
      </main>
    </div>
  );
}

export default App;