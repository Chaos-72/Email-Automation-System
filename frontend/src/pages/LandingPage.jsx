
// Updated code

import React, { useState, useEffect } from "react";
import "../style/landing.css";
import ContactManager_2 from "../components/ContactManager_2";
import PromptAgent_2 from "../components/PromptAgent_2";

export default function LandingPage() {
  const [contactData, setContactData] = useState({
    fileName: "",
    sampleRows: [],
  });
  const [aiOutput, setAiOutput] = useState("");

  // Initialize AOS (Animate on scroll)
  useEffect(() => {
    const script = document.createElement("script")
    script.src = "https://unpkg.com/aos@2.3.4/dist/aos.js";
    script.onload = () => window.AOS && window.AOS.init({ duration: 900, once: false })
    document.body.appendChild(script);
  }, []);


  return (
    <div>
      {/* HERO */}
      <section className="landing-hero d-flex align-items-center">
        <div className="container">
          <div className="d-flex justify-content-between align-items-start mb-6">
            <div className="brand-logo text-white">
              <i className="fa fa-envelope"></i>
              <div>
                <div style={{ fontSize: "1.05rem", fontWeight: 800 }}>Mailify</div>
                <div
                  style={{
                    fontSize: ".85rem",
                    color: "rgba(255,255,255,0.85)",
                    marginTop: -2,
                  }}
                >
                  Email automation
                </div>
              </div>
            </div>
          </div>

          <div className="row align-items-center">
            <div className="col-md-7">
              <h1 className="hero-title">Intelligent Automation for Modern People.</h1>
              <p className="hero-sub">Mailify brings Email automation to your fingertips.</p>
              <div className="mt-4">
                <button className="cta-btn btn btn-dark me-3">Get Started</button>
                <button className="cta-btn btn cta-outline">Proceed</button>
              </div>
            </div>
            <div className="col-md-5 text-md-end mt-4 mt-md-0"></div>
          </div>
        </div>
      </section>

      {/* MAIN INTERACTION */}
      <section className="py-5">
        <div className="container">
          {/* 🆕 Block 1 Upload -> LEFT COLUMN */}
          <div className="row justify-content-start" data-aos="fade-right">
            <div className="col-lg-6">
              <h5 className="mb-3">
                Upload Contacts{" "}
                <span className="text-muted" style={{ fontSize: ".9rem" }}>
                  (CSV/Excel)
                </span>
              </h5>

              <div className="upload-card mb-3">
                <ContactManager_2
                  onUploadSuccess={(data) => setContactData(data)}
                />
              </div>
            </div>
          </div>
        </div>
        {/* Block-2 Ask AI -> Right alinged */}
        <div className="row justify-content-end" data-aos="fade-left">
          <div className="col-lg-6">
            <h5 className="mb-3">Ask AI</h5>
            <div className="ai-box mb-3">
              <PromptAgent_2 onAIResponse={(msg) => setAiOutput(msg)} />
            </div>
          </div>
        </div>

        {/* Block 3 Sample output -> Left aligned */}
        <div className="row justify-content-start " data-aos="fade-right">
          <div className="col-lg-6 ml-2">
            <h6 className="mt-4 mb-2">
              Sample records from {contactData?.fileName || ""}
            </h6>
            <div className="sample-preview p-3 bg-light rounded-4 shadow-sm">
              {contactData?.sampleRows && contactData.sampleRows.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-sm table-striped table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        {Object.keys(contactData.sampleRows[0]).map((key) => (
                          <th key={key}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {contactData.sampleRows.map((row, idx) => (
                        <tr key={idx}>
                          {Object.keys(row).map((key) => (
                            <td key={key}>{row[key]}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted mb-0">No records yet.</p>
              )}
            </div>
          </div>
        </div>

        {/*Block -4 AI Said RIGHT COLUMN */}
        <div className="row justify-content-end" data-aos="fade-left">
          <div className="col-lg-6">
            <h5 className="mt-4 mb-3">AI said...</h5>
            <div className="ai-box p-3 bg-light rounded-4 shadow-sm d-flex align-items-center justify-content-center">
              <p className="mb-0">{aiOutput || ""}</p>
            </div>
          </div>
        </div>
      </section >
    </div >
  );
}
