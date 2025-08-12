# Shemeta Sebil Finance

## Overview
Shemeta is an AI-powered platform for crop recommendation and buyer-farmer matching. It consists of a Django backend and a modern React frontend, designed to help farmers grow and sell smarter, leveraging data and machine learning.

## Features
- Crop recommendation using AI, geospatial data and regional kebele data
- Buyer-farmer matching system
- RESTful API backend (Django, DRF, JWT)
- Modern frontend (React, Vite, Tailwind CSS)
- Data analytics and visualization
- Secure authentication

## Project Structure
```
Shemeta/
├── backend/
│   └── marketplace/
│       ├── manage.py
│       ├── requirements.txt
│       ├── marketplace/ (Django project)
│       ├── crop/ (Django app)
│       └── user/ (Django app)
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   ├── package.json
│   └── ...
├── data/ (datasets)
├── models/ (ML models)
└── ...
```

## Backend (Django)
- Located in `backend/marketplace`
- Main apps: `crop`, `user`
- REST API with JWT authentication
- Requirements: see `requirements.txt`
- To run:
  ```powershell
  cd backend/marketplace
  ../venv/Scripts/python.exe manage.py runserver
  ```

## Frontend (React)
- Located in `frontend/`
- Built with Vite, React, Tailwind CSS
- Main entry: `src/App.tsx`
- To run:
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```

## Data & Models
- Various CSV and JSON files for crop, weather, and kebele data
- ML models for crop recommendation and analytics

## Setup
1. Clone the repo:
   ```powershell
   git clone https://github.com/edealasc/sebil_finance.git
   ```
2. Create and activate a Python virtual environment in `backend`:
   ```powershell
   cd backend
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install backend requirements:
   ```powershell
   cd marketplace
   pip install -r requirements.txt
   ```
4. Run backend server:
   ```powershell
   ../venv/Scripts/python.exe manage.py runserver
   ```
5. Setup frontend:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

## Contributing
Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change.

## License
MIT
