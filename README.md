# Planorama



Planorama is a smart travel planning backend powered by FastAPI and AI. It integrates user-generated itineraries, location data, weather, and route optimization into a seamless travel planning API.

> ⚠️ This project is under active development. Expect breaking changes until v1.0 is released.

---

## 🔗 Test the current Deployed Version
Test the current working version of Planorama on Render:<br>
[Backend](https://planorama-9mr0.onrender.com)<br>
[Frontend](https://planorama-1.onrender.com) (Start up the Backend first, then you can use the frontend)<br><br>

---

## 🚀 Tech Stack

| Layer              | Tech                                               |
|--------------------|----------------------------------------------------|
| Backend            | FastAPI, SQLAlchemy, Pydantic                      |
| Frontend           | React, MUI                                         |
| Database           | PostgreSQL, Alembic                                |
| Auth               | JWT (manual)                                       |
| AI Services        | Sonar reasoning Ai, OpenRouteServices, Open-Meteo  |
| DevOps             | Docker (planned), Render, .env configs             |
| Testing (Planned)  | Pytest, pre-commit, Pylint                         |
| Docs (Planned)     | Sphinx, Markdown                                   |

---

## 📁 Project Structure (In Progress)

<details>
<summary>Click to expand</summary>
<br>
> 📁 Folders like `activities`, `auth`, `travel`, etc. follow a **feature module pattern**, each containing `api.py`, `models.py`, `schemas.py`, and `services.py` for separation of concerns.
<br>
<br>
project_root/<br>
├── app/  
│   ├── activities/  
│   │   ├── api.py  
│   │   ├── models.py  
│   │   ├── schemas.py  
│   │   └── services.py  
│   ├── auth/  # Feature module (api/models/schemas/services)  
│   │   └── ...  
│   ├── core/  
│   │   ├── config.py, database.py, security.py, ...  
│   ├── custom_docs/  # Custom OpenAPI docs logic  
│   │   └── api.py, services.py  
│   ├── external_services/  
│   │   ├── chatgpt.py, weather_api.py, ...  
│   │   └── connectors/  
│   │       └── openroute_connector.py  
│   ├── quotes/        # Feature module  
│   │   └── ...  
│   ├── stations/      # Feature module  
│   │   └── ...  
│   ├── travel/        # Feature module  
│   │   └── ...  
│   ├── trips/         # Feature module  
│   │   └── ...  
│   ├── users/         # Feature module  
│   │   └── ...  
│   ├── static/  
│   ├── templates/  
│   ├── utils/  
│   ├── __init__.py  
│   └── main.py  
├── docker/  
│   ├── development/  
│   ├── postgres/  
│   └── production/  
├── frontend/  
│   └── react/  
│       ├── public/  
│       │   ├── vite.svg  
│       │   └── images/  
│       │       └── home_background.jpg  
│       └── src/  
│           ├── assets/  
│           │   └── react.svg  
│           ├── components/  
│           │   ├── Navbar.jsx  
│           │   ├── PrivateRoute.jsx  
│           │   ├── Sidebar.jsx  
│           │   └── common/  
│           │       ├── AiSuggestions.jsx  
│           │       ├── TabbedModal.jsx  
│           │       └── WeatherWidget.jsx  
│           ├── context/  
│           │   └── AuthContext.jsx  
│           ├── I18n/  
│           │   ├── de.json  
│           │   └── en.json  
│           ├── pages/  
│           │   ├── AddStationPage.jsx  
│           │   ├── DashBoardPage.jsx  
│           │   ├── HomePage.jsx  
│           │   ├── LoginPage.jsx  
│           │   ├── RegisterPage.jsx  
│           │   ├── ReorderStationsPage.jsx  
│           │   ├── SettingsPage.jsx  
│           │   ├── TripsCreationPage.jsx  
│           │   ├── TripsGenerationPage.jsx  
│           │   └── TripsPage.jsx  
│           ├── app.css  
│           ├── app.jsx  
│           ├── config.js  
│           ├── i18n.js  
│           ├── index.css  
│           └── main.jsx  
├── migrations/  
│   ├── versions/  
│   ├── env.py  
│   ├── README  
│   └── script.py.mako  
├── tests/  
│   ├── test_auth.py  
│   └── test_trip.py  
├── .env / .env.example  
├── .gitignore  
├── .pylintrc  
├── alembic.ini  
├── LICENSE  
├── pre-commit-config.yaml  
├── pyproject.toml  
├── README.md  
└── requirements.txt  


</details>

<br>

---

## 🔧 Setup (Development)

```bash
# Clone the repo
git clone https://github.com/Theladron/planorama.git
cd planorama

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run the app
uvicorn app.main:app --reload

# Open a second terminal and run the frontend simultaneously
cd frontend/react
npm install
npm run dev
```

---

## 📌 Roadmap

* [x] FastAPI scaffolding

* [x] SQLAlchemy models

* [x] JWT authentication

* [x] Auth0 integration

* [x] React MUI frontend

* [ ] Pytest coverage

* [x] AI suggestion generation

* [x] AI route generation

* [ ] Sphinx docs

* [x] Render deployment

* [ ] Dockerization

---

## 🤝 Contributing

    Contributions are allways welcome! Especially in the frontend, my proficiency with React is limited and suggestions are welcome.
    Please fork the repo, create a feature branch, and submit a pull request to dev. Use conventional commit messages and make sure all tests pass.

---

## 🪪 License

This project is licensed under the Attribution-NonCommercial 4.0 International License.