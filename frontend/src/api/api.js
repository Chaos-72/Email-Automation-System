import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const analyzePrompt = async (prompt) => {
  const res = await API.post("api/ai/analyze", { prompt });
  return res.data;
};


// export async function createEvent(eventData) {
//   const res = await fetch("http://127.0.0.1:8000/api/event/create", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(eventData),
//   });
//   return res.json();
// }

// Updated create event

export async function createEvent(eventData) {
  try {
    // use axios.post so we can easily access reposen status & data on erro
    const res = await API.post("api/event/create", eventData, {
      headers: {"Content-Type": "application/json"},
    });
    // return JSON body (success)
    return res.data

  } catch {
    // IF server returned validation or other error, err.response exists
    if(err.response) {
      // throw an Error onject that includes the server response for the UI to show
      const e = new Error("Server validation failed");
      e.serverData = err.response.data;
      e.status = err.response.status;
      throw e;
    }
    throw err; // network or other error
  }
}


export const sendEmail = async (details) => {
  const res = await API.post("api/email/send", {
    subject: details.subject,
    body_html: details.body_html,
    recipients: details.recipients,
  });
  return res.data;
};


// New : Upload contact file

export async function uploadContacts(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post("api/contacts/upload", formData, {
    headers: {"content-type": "multipart/form-data"},
  });

  return res.data;
}

// New: Fetch contacts

export async function lookupContact(name) {
  const res = await API.get(`api/contacts/lookup/${name}`);
  return res.data;
}