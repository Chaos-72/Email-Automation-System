import React, { useState } from "react";
import { uploadContacts } from "../api/api";

export default function ContactManager_2({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // parse first 10 rows from uploaded CSV locally
  const parseCSV = (text) => {
    const lines = text.split("\n").filter(Boolean);
    const headers = lines[0].split(",");
    const rows = lines.slice(1, 11).map((line) => {
      const cols = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h.trim(), cols[i]?.trim()]));
    });
    // setSampleRows(rows);
    return rows;

  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const res = await uploadContacts(file);
      setUploadResult(res);
      
      // read locally for preview
      const text = await file.text();
      const rows = parseCSV(text);

      onUploadSuccess && onUploadSuccess({ fileName: file.name, sampleRows: rows }); // notify parent
    } catch (err) {
      console.error(err);
      setError("Upload failed. Please check file format (CSV/Excel).");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-panel p-3 rounded-4 shadow-sm bg-light">
      <form onSubmit={handleUpload}>
        <label className="form-label fw-semibold mb-2">
          Upload CSV or Excel file
        </label>
        <div className="input-group mb-3">
          <input
            type="file"
            accept=".csv, .xlsx, .xls"
            className="form-control"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <button
            className="btn btn-success"
            type="submit"
            disabled={loading || !file}
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </form>

      {uploadResult && (
        <div className="alert alert-success py-2">
          {uploadResult.count} contacts uploaded successfully!
        </div>
      )}

      {error && <div className="alert alert-danger py-2">{error}</div>}

    </div>
  );
}
