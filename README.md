# Doctor Agentic App

---

## Overview

The **Doctor Agentic App** is a full-stack application for doctor appointment scheduling. The backend is built with **FastAPI** and uses **PostgreSQL** for data storage. The frontend is developed with **React** and styled using **TailwindCSS**. The app helps manage doctor availability, schedule appointments, and send notifications via **Google Calendar** and **Gmail APIs**.

---

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL 
- **Frontend**: React, TailwindCSS
- **Other**: Pydantic, Requests, Google APIs (Calendar, Gmail)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nachiket-2024/doctor_agentic_app.git
cd doctor_agentic_app
```

### 2. Set up the environment

Install Backend dependencies with pip:

```bash
pip install -r requirements.txt
```

Install Frontend dependencies:

```bash
cd frontend
npm install
```

---

## Run the App

### 1. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload
```

### 2. Run the React frontend

```bash
cd frontend
npm run dev
```

---

## .env Setup

Make a `.env` file at the root of the project (doctor_agentic_app) with the following content:

```ini
# Postgresql Database URL
DATABASE_URL=postgresql://username:password@localhost:5432/doctor_agentic_db

# JWT Secret Key used for signing tokens
JWT_SECRET=jwt_secret_key_here

ACCESS_TOKEN_EXPIRE_MINUTES=minutes_in_numbers_here
REFRESH_TOKEN_EXPIRE_DAYS=time_in_days_here

# Google OAuth2 Credentials
GOOGLE_CLIENT_ID=google_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
GOOGLE_TOKEN_FILE=token.json

# Admin Email (Currently only 1 email has been used for basic and clear set up)
ADMIN_EMAILS=admin_email_here
```

---
