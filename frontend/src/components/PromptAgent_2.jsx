// import React, { useState } from "react";
// import { analyzePrompt, createEvent, lookupContact, sendEmail } from "../api/api";

// export default function PromptAgent_2({ onAIResponse }) {
//   const [prompt, setPrompt] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setLoading(true);
//     setError("");

//     try {
//       const aiResponse = await analyzePrompt(prompt);
//       const { intent, details } = aiResponse.parsed;
//       let finalMsg = "";

//       if (intent === "create_event") {
//         if (!details.datetime || isNaN(new Date(details.datetime))) {
//           setError("Could not determine time — please specify a date/time more precisely.");
//           return;
//         }

//         const start = new Date(details.datetime);
//         const end = new Date(start.getTime() + 60 * 60 * 1000);

//         // 1. Normalize attendees array input
//         const rawAttendees = details.attendees || [];   // may be names or emails
        
//         // 2. Resolve non-email attendees via contact look up
//         const resolved = await Promise.all(
//           rawAttendees.map(asyn (a) => {
//             if (typeof a !== "string") return null;
//             const trimmed = a.trim();
//             if (trimmed.includes("@")) return trimmed; // already email
//             // not an email -> contact look up

//             try {
//               const constact = await lookupContact(encodeURIComponent(trimmed));
//               // contact is { name, email }
//               return constact.email;

//             } catch (err) {
//               // lookup failed 
//               return null;
//             }
//           })
//         );
      
//   const cleanDetails = {
//     title: details.title || "Untitled Event",
//     start_iso: start.toISOString(),
//     end_iso: end.toISOString(),
//     attendees: details.attendees || [],
//   };

//   const eventRes = await createEvent(cleanDetails);
//   finalMsg = eventRes.ok
//     ? `Event "${cleanDetails.title}" scheduled for ${start.toLocaleString()}.`
//     : "Failed to create event.";




// } else if (intent === "send_email") {
//   const cleanEmail = {
//     subject: details.subject || "No Subject",
//     body_html: details.body_html || details.body || "<p>No content</p>",
//     recipients: Array.isArray(details.to)
//       ? details.to
//       : [details.to || "unknown@domain.com"],
//   };

//   const resolveRecipients = await Promise.all(
//     cleanEmail.recipients.map(async (r) => {
//       if (!r.includes("@")) {
//         try {
//           const c = await lookupContact(r);
//           return c.email || r;
//         } catch {
//           return r;
//         }
//       }
//       return r;
//     })
//   );

//   cleanEmail.recipients = resolveRecipients;
//   const res = await sendEmail(cleanEmail);
//   finalMsg = res.ok
//     ? `Email sent successfully to ${cleanEmail.recipients.join(", ")}.`
//     : "Failed to send email.";
// } else {
//   finalMsg = "I’m not sure what you meant. Please try again.";
// }

// onAIResponse(finalMsg);
//     } catch (err) {
//   console.error(err);
//   setError(err.message || "Something went wrong.");
// } finally {
//   setLoading(false);
// }
//   };

// return (
//   <div className="ai-panel p-3 rounded-4 shadow-sm bg-light">
//     <form onSubmit={handleSubmit}>
//       <label className="form-label fw-semibold mb-2">
//         Ask AI to automate your task
//       </label>
//       <textarea
//         className="form-control mb-3"
//         rows="3"
//         placeholder="e.g. Send email to Ravi about tomorrow’s meeting..."
//         value={prompt}
//         onChange={(e) => setPrompt(e.target.value)}
//         required
//       ></textarea>
//       <div className="text-end">
//         <button
//           className="btn btn-primary px-4"
//           type="submit"
//           disabled={loading}
//         >
//           {loading ? "Thinking..." : "Ask AI"}
//         </button>
//       </div>
//     </form>
//     {error && <div className="alert alert-danger mt-2">{error}</div>}
//   </div>
// );
// }





// ==================
// 
//  Update code
// 
// ==================

import React, {useState} from "react";
import { analyzePrompt, createEvent, lookupContact, sendEmail } from "../api/api";
import { useAsyncError } from "react-router-dom";

export default function PromptAgent_2({onAIResponse}) {

  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Ask backend to analyse the prompt
      const aiResponse = await analyzePrompt(prompt);
      const { intent, details } = aiResponse.parsed || {};
      let finalMsg = "";

      // -----------
      // Case 1: Create calendat Event
      // -----------

      if (intent === "create_event") {
        if(!details.datetime || isNaN(new Date(details.datetime))) {
          setError("Could not determine time - please specify a date/time more precisely.");
          setLoading(true);
          return;
        }
        const start = new Date(details.datetime);
        const end = new Date(start.getTime() + 60 * 30 *1000); // Assuming each event of 1 hr

        // 1. Normalize attendees (names or emails)
        const rawAttendees = details.attendees || [];

        // 2. Resolve attendees -> valid email address
        const resolved = await Promise.all(
          rawAttendees.map(async (a)=> {
            if (typeof a !== "string") return null;
            const trimmed = a.trim();
            if (trimmed.includes("@")) return trimmed; // already an email
            try {
              const contact = await lookupContact(encodeURIComponent(trimmed));
              return contact.email || null;

            } catch(err) {
              console.warn(`Could not resolve contact for: ${trimmed} `);
              return null
            }
          })
        );

        const attendeesResolved = Array.from(new Set(resolved.filter(Boolean)));

        // 3. Check for unresolved names
        const unresolved = rawAttendees.filter((_, i) => !resolved[i]);
        if (unresolved.lenght > 0) {
          setError(
            `Could not resolve theese attendees: ${unresolved.join(", ")}.
             Please upload matching contacts or provide emails.`
          );
          setLoading(false);
          return;
        }

        // 4. Prepare event data
        const cleanDetails = {
          title: details.title || "Untitled Event",
          start_iso: start.toISOString(),
          end_iso: end.toISOString(),
          attendees: attendeesResolved,
          cancel_conflicts: true,
          notify: true,
        };

        // 5. Call backend API
        try {
          const eventRes = await createEvent(cleanDetails);
          finalMsg = eventRes.ok
          ? `Event "${cleanDetails.title}" scheduled for ${start.toLocaleString()}.`
          : "Event created successfully (validation OK).";
        } catch(err) {
          console.error("Event creation failed: ", err);
          if (err.serverData) {
            setError(
              `Event creation failed: ${JSON.stringify(err.serverData.details || err.serverData)}`
            );

          } else {
            setError("Failed to create event. Please check you data.");
          }
          setLoading(false);
          return;
        }
      }
      else if (intent === "send_email") {
        const rawRecipients = Array.isArray(details.to)
          ? details.to
          : [details.to || ""];

          // Resolve names to emails
          const resolveRecipients = await Promise.all(
            rawRecipients.map(async (r) => {
              const s = (r || "").trim();
              if (s.includes("@")) return s;
              try {
                const c = await lookupContact(encodeURIComponent(s));
                return c.email;
              } catch {
                console.warn(`Could not find email for ${s}`);
                return null
              }
            })
          );

          const validRecipients = resolveRecipients.filter(Boolean);
          const unresolved = rawRecipients.filter((_, i) => !resolveRecipients[i]);

          if (unresolved.lenght > 0) {
            setError(
              `Could not find emails for: ${unresolved.join(", ")}.
              Please upload contacts or specify full emails.`
            );
            setLoading(false);
            return;
          }

          const cleanEmail = {
            subject: details.subject || "No Subject",
            body_html: details.body_html || details.body || "<p>No content</P",
            recipients: validRecipients,
          };

          try {
            const res = await sendEmail(cleanEmail);
            finalMsg = res.ok
              ? `Email sent successfully to ${cleanEmail.recipients.join(", ")}.`
              : "Failed to send email."
          } catch(err) {
            console.error("Email sending failled:", err);
            if(err.serverData) {
              setError(`Email failed: ${JSON.stringify(err.serverData)}`);
            } else {
              setError("Failed to send email. Please check recipients.");
            }
            setLoading(false);
            return;
          }
      }

      // Other unknown intent
      else {
        finalMsg = "I am not sure what you meant. Please try again.";
      }

      // output message to parent
      onAIResponse(finalMsg);

    } catch(err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="ai-panel p-3 rounded-4 shadow-sm bg-light">
      <form onSubmit={handleSubmit}>
        <label className="form-label fw-semibold mb-2">
          Ask AI to automate your task
        </label>
        <textarea
          className="form-control mb-3"
          rows="3"
          placeholder="e.g. Send emailt to Ravi about tommorrow's meeting..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          required
        ></textarea>
        <div className="text-end">
          <button className="btn btn-primary px-4" type="submit" disabled = {loading}>
            {loading ? "Thinking...": "Ask AI"}
          </button>
        </div>
      </form>
      {error && <div className="alter alert-danger mt-2">{error}</div>}
    </div>
  );  

}