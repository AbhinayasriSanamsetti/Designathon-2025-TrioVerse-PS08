import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTextSubmit = async (event) => {
    event.preventDefault();
    if (!text) {
      alert("Please enter some text!");
      return;
    }
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:5000/predict_text", { text });
      setResult(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("Error processing request!");
    }

    setLoading(false);
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileSubmit = async () => {
    if (!file) {
      alert("Please upload an image or video!");
      return;
    }
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      let endpoint = file.type.startsWith("image/")
        ? "http://127.0.0.1:5000/predict_image"
        : "http://127.0.0.1:5000/predict_video";

      const response = await axios.post(endpoint, formData, { headers: { "Content-Type": "multipart/form-data" } });
      setResult(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("Error processing request!");
    }

    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Fake News Detector</h1>

      <form onSubmit={handleTextSubmit}>
        <label>Enter News Text:</label>
        <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Enter news text here..." />
        <button type="submit" disabled={loading}>{loading ? "Checking..." : "Check Text"}</button>
      </form>

      <label>Upload Image or Video:</label>
      <input type="file" accept="image/,video/" onChange={handleFileChange} />
      <button onClick={handleFileSubmit} disabled={loading}>{loading ? "Uploading..." : "Upload File"}</button>

      {result && (
        <div>
          <h2>Prediction Result:</h2>
          <p><b>Prediction:</b> {result.prediction || "N/A"}</p>
          <p><b>Confidence:</b> {result.confidence || "N/A"}%</p>
        </div>
      )}
    </div>
  );
}

export default App;