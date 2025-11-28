import React, { useState } from "react";
import { analyzePrompt, createEvent, lookupContact, sendEmail } from "../api/api";

export default function PromptAgent() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [responseMsg, setResponseMsg] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResponseMsg(null);

    try {
      // 1️⃣ Analyze intent
      const aiResponse = await analyzePrompt(prompt);
      const { intent, details } = aiResponse.parsed;

      let finalMsg = "";

      // Adjust event payload for backend compatibility
      if (intent === "create_event") {

        // Re-ask the model to clarify the time
        if (!details.datetime || isNaN(new Date(details.datetime))) {
          setError("Could not determine time — please specify a date/time more precisely.");
          return;
        }
        // We'll assume the AI gives you one datetime (start time)
        // We'll add 1 hour for end time automatically
        const start = new Date(details.datetime);
        const end = new Date(start.getTime() + 60 * 60 * 1000); // +1 hour

        const cleanDetails = {
          title: details.title || "Untitled Event",
          start_iso: start.toISOString(),
          end_iso: end.toISOString(),
          attendees: details.attendees || [],
          cancel_conflicts:
            details.cancel_conflicts !== undefined
              ? details.cancel_conflicts
              : true,
          notify: true,
          recurrence: details.recurrence || null, // Support for recurrence if provided
        };

        const eventRes = await createEvent(cleanDetails);
        if (eventRes.ok) {
          finalMsg = `Event "${cleanDetails.title}" scheduled for ${start.toLocaleString()}.`;
        } else {
          throw new Error("Failed to create event");
        }
      }

      // Handle send_email intent
      else if (intent === "send_email") {

        // Fix payload mismatch
        const cleanEmail = {
          subject: details.subject || "No Subject",
          body_html: details.body_html || details.body || "<p>No content</p>",
          recipients: Array.isArray(details.to)
            ? details.to
            : details.recipients
              ? details.recipients
              : [details.to || "unknown@domain.com"]
        };

        // New Code: Resolve contact names -> email address before sending
        const resolveRecipients = await Promise.all(
          cleanEmail.recipients.map(async (recipient) => {
            // only lookup if recepient in NOT already an email address
            if (!recipient.includes("@")) {
              try {
                const contactData = await lookupContact(recipient); // call -> api/contacts/lookup{name}
                return contactData.email || recipient; // fallback to the same string
              }
              catch {
                console.warn(`No contact found for "${recipient}" - skiping lookup`);
                return recipient; // fallback to the same string
              }
            }
            return recipient; // already a valid email
          })
        );

        // Replace recipents with resolve
        cleanEmail.recipients = resolveRecipients;

        // Now send the email
        const emailRes = await sendEmail(cleanEmail);
        if (emailRes.ok) {
          finalMsg = `Email sent successfully to ${cleanEmail.recipients.join(",") || details.recipients?.join(", ")}.`;
        } else {
          throw new Error("Failed to send email");
        }
      }

      // Unknown or Unsupported intent
      else {
        finalMsg =
          "🤖 I’m not sure what you meant. Please try rephrasing your request.";
      }
      setResponseMsg(finalMsg);

    } catch (err) {
      console.error("Error:", err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(`Backend validation failed: ${JSON.stringify(err.response.data.detail)}`);
      } else {
        setError(`${err.message || "Something went wrong. Please try again."}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5" style={{ maxWidth: "700px" }}>
      <div className="card shadow-lg border-0 rounded-4">
        <div className="card-body p-5">
          <h2 className="text-center mb-4 fw-bold text-primary">
            🤖 Email & Calendar Assistant
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <textarea
                className="form-control p-3 fs-5 rounded-4 shadow-sm"
                rows="3"
                placeholder="Ask me anything... e.g., 'Schedule a meeting tomorrow at 10 AM and email the team'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                required
              />
            </div>

            <div className="text-center">
              <button
                className="btn btn-primary btn-lg rounded-4 px-5"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span
                      className="spinner-border spinner-border-sm me-2"
                      role="status"
                    ></span>
                    Thinking...
                  </>
                ) : (
                  "Ask AI"
                )}
              </button>
            </div>
          </form>

          {/* Feedback section */}
          <div className="mt-4 text-center">
            {error && <div className="alert alert-danger">{error}</div>}
            {responseMsg && (
              <div className="alert alert-success fw-semibold fs-5">
                {responseMsg}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
