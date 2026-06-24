# 🛡️ National Intelligence & Crime Records System (NICRS)

**Repository Link:** [https://github.com/Kartellxrd/Police-](https://github.com/Kartellxrd/Police-)  
**Target Architecture:** Next.js (Pure JavaScript + Tailwind CSS) + Python (FastAPI) + PostgreSQL via Supabase  
**Development Workspace:** GitHub Codespaces (PC/Browser Deployment)

---

## 👥 Core Project Team & Work Distribution
* **Backend Engineering & Database Architecture:** `@Kartellxrd` (Working on Backend Subsystems)
* **Frontend Interface & UI/UX Experience:** `Sedie` (Working on Frontend UI Pages)

---

## 📁 Repository Structure Blueprint
```text
Police- /
├── frontend/                 <-- Next.js Frontend Application Workspace (Sedie)
│   ├── src/
│   │   ├── components/       <-- Reusable layout blocks (Navbar, Alert banners)
│   │   └── pages/            <-- App routes (index.js, login.js, search.js)
│   ├── package.json
│   └── tailwind.config.js
│
└── backend/                  <-- FastAPI Backend Application Workspace (Kartellxrd)
    ├── app/
    │   ├── main.py           <-- Core API entrypoint & route management binder
    │   ├── database.py       <-- Connection engine pooler to Supabase PostgreSQL
    │   ├── models.py         <-- Database tables mapping schema
    │   ├── schemas.py        <-- Incoming data validation guardrails
    │   └── routers/          <-- Modular router processing endpoints
    │       ├── auth.py       <-- /auth paths (Staff account sessions)
    │       ├── suspects.py   <-- /suspects paths (Omang verification profiles)
    │       └── crimes.py     <-- /crimes paths (Incident logging engines)
    ├── .env                  <-- Hidden database credential variables
    └── requirements.txt      <-- Python environment libraries
