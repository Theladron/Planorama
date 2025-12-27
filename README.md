# Planorama



Planorama is a smart travel planning backend powered by FastAPI and AI. It integrates user-generated itineraries, location data, weather, and route optimization into a seamless travel planning API.

> ⚠️ This project is not under active development anymore. Please expect irregular updates and responses to outside contribution.

---

## 🔗 Test the current Deployed Version
Test the current working version of Planorama on Amazon AWS EC2:<br>
[Backend](http://13.51.172.110:8000/api/docs)<br>
[Frontend](http://13.51.172.110:5173/)<br><br>

---

## 🚀 Tech Stack

| Layer              | Tech                                               |
|--------------------|----------------------------------------------------|
| Backend            | FastAPI, SQLAlchemy 2.0, Pydantic 2.x             |
| Frontend           | React 19, Vite, MUI, React Router                 |
| Database           | PostgreSQL, Alembic, SQLite (testing)             |
| Auth               | JWT (PyJWT), Argon2 password hashing               |
| AI Services        | Sonar AI, OpenRouteService, Open-Meteo            |
| Testing            | Pytest, pytest-cov, Jest, React Testing Library  |
| Docs               | Sphinx                                             |
| DevOps             | Docker, Docker Compose, Render                     |
| Code Quality       | Pylint, ESLint, pre-commit                        |

---

## 📁 Project Structure

<details>
<summary>Click to expand</summary>
<br>
> 📁 Folders like `activities`, `auth`, `travel`, etc. follow a **feature module pattern**, each containing `api.py`, `models.py`, `schemas.py`, and `services.py` for separation of concerns.
<br>
<br>
project_root/<br>
├── app/<br>
│   ├── activities/          # Feature module<br>
│   │   ├── api.py, models.py, schemas.py, services.py<br>
│   ├── auth/                # Feature module<br>
│   │   ├── api.py, models.py, services.py<br>
│   ├── core/                # Core configuration<br>
│   │   ├── config.py, database.py, security.py<br>
│   │   ├── config_loader.py, connector_loader.py<br>
│   │   └── logging_config.py, seed.py<br>
│   ├── custom_docs/         # Custom OpenAPI docs<br>
│   │   └── api.py, services.py<br>
│   ├── external_services/    # External API integrations<br>
│   │   ├── ai_suggestions.py, weather_api.py<br>
│   │   ├── googletrans.py, openroute.py<br>
│   │   ├── connectors/      # Connector abstractions<br>
│   │   │   ├── ai_connector.py<br>
│   │   │   ├── googletrans_connector.py<br>
│   │   │   ├── openroute_connector.py<br>
│   │   │   └── weather_api_connector.py<br>
│   │   └── service_routes/  # Service route handlers<br>
│   ├── quotes/              # Feature module<br>
│   │   └── api.py, models.py, schemas.py, services.py<br>
│   ├── stations/            # Feature module<br>
│   │   └── api.py, models.py, schemas.py, services.py<br>
│   ├── travel/              # Feature module<br>
│   │   └── api.py, models.py, schemas.py, services.py<br>
│   ├── trip_stations/       # Junction table module<br>
│   │   └── models.py, schemas.py, services.py<br>
│   ├── trips/               # Feature module<br>
│   │   └── api.py, models.py, schemas.py, services.py<br>
│   ├── users/               # Feature module<br>
│   │   └── api.py, models.py, schemas.py, services.py<br>
│   ├── tests/               # Test suite<br>
│   │   ├── conftest.py      # Pytest fixtures<br>
│   │   ├── integration/     # Integration tests<br>
│   │   │   ├── test_auth_api.py<br>
│   │   │   └── test_trips_api.py<br>
│   │   └── unit/            # Unit tests<br>
│   │       ├── test_auth_services.py<br>
│   │       ├── test_security.py<br>
│   │       ├── test_travel_services.py<br>
│   │       ├── test_trip_stations_services.py<br>
│   │       ├── test_trips_services.py<br>
│   │       └── test_users_services.py<br>
│   ├── __init__.py<br>
│   └── main.py<br>
├── frontend/<br>
│   └── react/<br>
│       ├── public/<br>
│       │   └── images/<br>
│       ├── src/<br>
│       │   ├── api/         # API client modules<br>
│       │   ├── components/  # React components<br>
│       │   │   ├── common/<br>
│       │   │   └── trips/<br>
│       │   ├── context/     # React context providers<br>
│       │   ├── hooks/       # Custom React hooks<br>
│       │   ├── i18n/        # Internationalization<br>
│       │   ├── pages/       # Page components<br>
│       │   ├── utils/       # Utility functions<br>
│       │   └── main.jsx, App.jsx<br>
│       ├── tests/           # Frontend tests<br>
│       ├── package.json<br>
│       └── vite.config.js<br>
├── migrations/              # Alembic migrations<br>
│   ├── versions/<br>
│   ├── env.py<br>
│   └── script.py.mako<br>
├── docs/                    # Sphinx documentation<br>
│   ├── conf.py<br>
│   └── index.rst<br>
├── scripts/                 # Utility scripts<br>
│   └── run-all-tests.sh<br>
├── alembic.ini<br>
├── docker-compose.yml<br>
├── Dockerfile.test<br>
├── pytest.ini<br>
├── pyproject.toml<br>
├── requirements.txt<br>
└── README.md<br>

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

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials and API keys

# Set up database (PostgreSQL)
# Create database and update DATABASE_URL in .env

# Run migrations
alembic upgrade head

# Run the backend
uvicorn app.main:app --reload

# In a separate terminal, run the frontend
cd frontend/react
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
pytest

# Backend tests with coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend/react
npm test

# Frontend tests with coverage
npm run test:coverage
```

---

## 📌 Roadmap

### Completed ✅

* [x] FastAPI scaffolding with feature module architecture
* [x] SQLAlchemy 2.0 models with proper relationships
* [x] JWT authentication with Argon2 password hashing
* [x] React 19 frontend with Vite and MUI
* [x] Comprehensive test suite (pytest + Jest)
* [x] Test coverage reporting (56% backend, improving)
* [x] AI suggestion generation (Sonar AI)
* [x] Route optimization (OpenRouteService)
* [x] Weather integration (Open-Meteo)
* [x] Sphinx documentation
* [x] Docker and Docker Compose setup
* [x] Render deployment
* [x] Database migrations (Alembic)
* [x] Internationalization (i18n)
* [x] Code quality tools (Pylint, ESLint, pre-commit)

---

## 🤝 Contributing

    Contributions are allways welcome! Especially in the frontend, my proficiency with React is limited and suggestions are welcome.
    Please fork the repo, create a feature branch, and submit a pull request to dev. Use conventional commit messages and make sure all tests pass.

---

## 🪪 License

This project is licensed under the Attribution-NonCommercial 4.0 International License.