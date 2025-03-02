import { useState } from "react";

export default function FakeNewsDetection() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

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

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      alert("Error processing request!");
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h2>Analyze Uploaded Media</h2>

      <label>Upload Image or Video</label>
      <input type="file" accept="image/*, video/*" onChange={handleFileChange} />

      <button onClick={handleFileSubmit} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Media"}
      </button>

      {result && (
        <div className={`result-box ${result.is_fake ? "result-fake" : "result-real"}`}>
          <h3>{result.is_fake ? "Fake News Detected!" : "Real News"}</h3>
          <p>Confidence Score: <strong>{result.confidence}</strong></p>
        </div>
      )}
    </div>
  );
}
