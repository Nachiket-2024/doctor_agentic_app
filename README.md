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
