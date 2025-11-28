import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import Assistant from "./components/PromptAgent";
import Contacts from "./components/ContactManager";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/contacts" element={<Contacts />} />
      </Routes>
    </BrowserRouter>
  );
}



// import React, { useState } from "react";
// import PromptAgent from "./components/PromptAgent";
// import ContactManager from "./components/ContactManager";

// export default function App() {
//   const [activeTab, setActiveTab] = useState("agent");

//   return (
//     <div>
//       <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
//         <div className="container">
//           <a className="navbar-brand fw-bold text-primary" href="#">
//             🧠 Smart Assistant
//           </a>
//           <ul className="navbar-nav ms-auto">
//             <li className="nav-item me-3">
//               <button
//                 className={`btn ${
//                   activeTab === "agent" ? "btn-primary" : "btn-outline-primary"
//                 } rounded-4`}
//                 onClick={() => setActiveTab("agent")}
//               >
//                 Assistant
//               </button>
//             </li>
//             <li className="nav-item">
//               <button
//                 className={`btn ${
//                   activeTab === "contacts"
//                     ? "btn-success"
//                     : "btn-outline-success"
//                 } rounded-4`}
//                 onClick={() => setActiveTab("contacts")}
//               >
//                 Contacts
//               </button>
//             </li>
//           </ul>
//         </div>
//       </nav>

//       {/* Main content */}
//       {activeTab === "agent" && <PromptAgent />}
//       {activeTab === "contacts" && <ContactManager />}
//     </div>
//   );
// }
