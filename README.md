[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestration-brightgreen)](https://python.langchain.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-API-ffca28?logo=googlegemini)](https://ai.google.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-UI-38BDF8?logo=tailwindcss)](https://tailwindcss.com/)

# **📧 Email & Calendar Automation System**

Automated email sending, meeting scheduling, and intelligent date reasoning powered by LLMs, FastAPI, and React.

---

## *🧠 Project Overview*

This system automates *email sending, **meeting scheduling, and **CRM contact lookup* using an AI-powered workflow.

The user simply uploads a *contact CSV* (CRM file containing names, emails, roles, etc.) and interacts through natural language.
The AI handles fuzzy search, email generation, recipient detection, and event scheduling.

---

## *✨ Key Features*

### 🔹 *1. Smart CRM CSV Processing*

* User uploads a CRM CSV containing customer/employee data.
* System parses and stores it for quick search.
* Supports *fuzzy name matching* (typos tolerated).

### 🔹 *2. Natural Language Email Automation*

Example:
*“Send an email to Rohan about tomorrow’s delivery.”*
System will:

1. Find Rohan in CRM (even if typed “Rohen”).
2. Generate the email using the LLM.
3. Send the email automatically.
4. Display success message on UI.

### 🔹 *3. Intelligent Meeting Scheduling*

User request:
*“Schedule a meeting tomorrow at 10 PM with the project team.”*
System will:

* Identify all members belonging to the project team from CRM.
* Create a meeting payload.
* Send meeting invites to each person.
* Show a confirmation on UI.

### 🔹 *4. Real-Time Event Date Understanding*

The model uses real-time reasoning like:

✔ *“Schedule meeting after Diwali.”*
→ Automatically finds the date of Diwali for the current year
→ Schedules next-day meeting (21 Oct if Diwali is on 20 Oct)

✔ If the event has already passed:
*Asked in December: “Schedule after Holi.”*
→ Looks for Holi in next year
→ Correctly schedules for 2026.

### 🔹 *5. Full-Stack Application*

* *Frontend:* React + Tailwind
* *Backend:* FastAPI
* *Orchestration:* LangChain
* *LLM Brain:* Gemini API
* Clean UI with real-time responses.

---

## 🛠 *Tech Stack*

### *Frontend*

* React
* Tailwind CSS
* Axios

### *Backend*

* FastAPI
* Python
* LangChain

### *AI / APIs*

* Google Gemini API (Primary LLM)

---

## 📁 *Project Structure*

```
Email_Automation_System/
│
│── backend/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── scheduler.py
│   ├── google_auth_flow.py
│   ├── google_utils.py
│   ├── credentials.json        (ignored by .gitignore)
│   ├── token.json              (ignored by .gitignore)
│   │
│   ├── routes/
│   │   ├── ai_routes.py
│   │   ├── contact_routes.py
│   │   ├── email_routes.py
│   │   └── event_routes.py
│   │
│   └── services/
│       ├── calendar_service.py
│       ├── contact_service.py
│       ├── email_service.py
│       └── llm_service.py
│
│── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   └── LandingPage.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ContactManager.jsx
│   │   │   ├── ContactManager_2.jsx
│   │   │   ├── PromptAgent.jsx
│   │   │   └── PromptAgent_2.jsx
│   │   └── style/
│   │       └── landing.css
│   │
│   ├── public/
│   │   ├── Mailify_logo.png
│   │   └── vite.svg
│   │
│   ├── contacts.csv
│   ├── package.json
│   ├── package-lock.json
│   ├── eslint.config.js
│   └── vite.config.js
│
│── example.env
│── requirements.txt
│── .gitignore
│── README.md
│
│── test_calendar_service.py
│── test_create_event.py
│── test_parse_intent.py
│── test_oauth_calendar.py
│
│── app.db                 (ignored)
│── client_secret.json     (ignored)
│── token.json             (ignored)
│── old creds/             (ignored)

```
---

## 🔐 *Environment Variables*

Create an example.env file:

```
GOOGLE_API_KEY=your-api-key
EMAIL_USER=your-email-id
EMAIL_PASSWORD=your-app-password
```

Rename example.env → *.env*
(Do NOT commit .env to GitHub)

---

## ▶ *Running the Backend*

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## ▶ *Running the Frontend*

```bash
cd frontend
npm install
npm run dev
```

---

## 💡 *Usage Examples*

### 👉 Send email

Send an email to Rakesh about the budget approval.

### 👉 Schedule a meeting

Schedule a meeting tomorrow at 2 PM with marketing team.

### 👉 Real-time event logic

Schedule a meeting after Diwali.


---