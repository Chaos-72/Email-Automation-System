import React, { useState } from "react";
import { uploadContacts, lookupContact } from "../api/api";

export default function ContactManager() {
  const [file, setFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [lookupName, setLookupName] = useState("");
  const [lookupResult, setLookupResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const res = await uploadContacts(file);
      setUploadResult(res);
    } catch (err) {
      console.error(err);
      setError("Upload failed. Check file format (CSV/Excel).");
    } finally {
      setLoading(false);
    }
  };

  const handleLookup = async (e) => {
    e.preventDefault();
    if (!lookupName.trim()) return;
    setLoading(true);
    setError("");
    setLookupResult(null);
    try {
      const res = await lookupContact(lookupName);
      setLookupResult(res);
    } catch (err) {
      setError("No match found for that name.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5" style={{ maxWidth: "700px" }}>
      <div className="card shadow-lg border-0 rounded-4">
        <div className="card-body p-4">
          <h2 className="text-center mb-4 fw-bold text-primary">
            📇 Contact Manager
          </h2>

          {/* File Upload */}
          <form onSubmit={handleUpload}>
            <div className="mb-3">
              <label className="form-label fw-semibold">
                Upload CSV or Excel file
              </label>
              <input
                type="file"
                accept=".csv, .xlsx, .xls"
                className="form-control rounded-4 shadow-sm"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </div>

            <div className="text-center">
              <button
                type="submit"
                className="btn btn-success btn-lg rounded-4"
                disabled={loading || !file}
              >
                {loading ? "Uploading..." : "Upload Contacts"}
              </button>
            </div>
          </form>

          {uploadResult && (
            <div className="alert alert-success mt-3">
              ✅ {uploadResult.count} contacts uploaded successfully!
            </div>
          )}

          {/* Lookup Section */}
          <hr className="my-4" />
          <form onSubmit={handleLookup}>
            <div className="mb-3">
              <label className="form-label fw-semibold">
                Search contact by name
              </label>
              <input
                type="text"
                className="form-control rounded-4 shadow-sm"
                placeholder="Enter name e.g., Ananya"
                value={lookupName}
                onChange={(e) => setLookupName(e.target.value)}
              />
            </div>

            <div className="text-center">
              <button
                className="btn btn-primary btn-lg rounded-4"
                type="submit"
                disabled={loading || !lookupName}
              >
                {loading ? "Searching..." : "Lookup"}
              </button>
            </div>
          </form>

          {lookupResult && (
            <div className="alert alert-info mt-3 text-center">
              <strong>{lookupResult.name}</strong> → {lookupResult.email}
            </div>
          )}

          {error && <div className="alert alert-danger mt-3">{error}</div>}
        </div>
      </div>
    </div>
  );
}
