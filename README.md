# Planorama



Planorama is a smart travel planning backend powered by FastAPI and AI. It integrates user-generated itineraries, location data, weather, and route optimization into a seamless travel planning API.

> ⚠️ This project is not under active development anymore. Please expect irregular updates and responses to outside contribution.

---

## 🔗 Live Demo
Test the current deployed version of Planorama:<br>
[Frontend](https://planorama.duckdns.org/) - Main application<br>
[Backend API Docs](https://planorama.duckdns.org/api/docs) - Interactive API documentation<br><br>

*Deployed on AWS EC2 with automated CI/CD via GitHub Actions*

---

## 🚀 Tech Stack

| Layer              | Tech                                              |
|--------------------|---------------------------------------------------|
| Backend            | FastAPI, SQLAlchemy 2.0, Pydantic 2.x             |
| Frontend           | React 19, Vite, MUI, React Router                 |
| Database           | PostgreSQL, Alembic, SQLite (testing)             |
| Auth               | JWT (PyJWT), Auth0                                |
| AI Services        | Sonar AI, OpenRouteService, Open-Meteo            |
| Testing            | Pytest, pytest-cov, Vitest, React Testing Library |
| Docs               | Sphinx                                            |
| DevOps             | Docker, Docker Compose, GitHub Actions            |
| CI/CD              | GitHub Actions (CI/CD workflows)                  |
| Deployment         | AWS EC2, DuckDNS, Let's Encrypt (HTTPS)           |
| Code Quality       | Pylint, ESLint                                    |

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
├── .github/<br>
│   └── workflows/          # GitHub Actions CI/CD<br>
│       ├── ci.yml          # Continuous Integration<br>
│       └── deploy.yml      # Deployment to AWS EC2<br>
├── .gitattributes          # Git line ending configuration<br>
├── alembic.ini<br>
├── docker-compose.yml      # Docker Compose configuration<br>
├── Dockerfile.test         # Test container Dockerfile<br>
├── app/Dockerfile          # Backend production Dockerfile<br>
├── frontend/react/Dockerfile # Frontend production Dockerfile<br>
├── pytest.ini<br>
├── pyproject.toml<br>
├── requirements.txt<br>
└── README.md<br>

</details>

<br>

---

## 🔧 Setup (Development)

### Option 1: Docker Compose (Recommended)

The easiest way to get started is using Docker Compose, which sets up all services (database, backend, frontend) automatically:

```bash
# Clone the repo
git clone https://github.com/Theladron/planorama.git
cd planorama

# Create .env file with your configuration
# Copy from .env.example and fill in your values:
# - Database credentials
# - Auth0 configuration
# - API keys (ORS_API_KEY, AI_API_KEY)

# Build and start all services
docker compose up

# Or run in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**Note**: The Docker Compose setup runs tests automatically before starting backend and frontend services (fail-fast approach).


### Running Tests

```bash
# Run all tests (backend + frontend)
docker compose run --rm test

# Or just start services - tests run automatically before backend/frontend start
docker compose up
```

## 📌 Roadmap

### Completed ✅

* [x] FastAPI scaffolding with feature module architecture
* [x] SQLAlchemy 2.0 models with proper relationships
* [x] Auth0 authentication
* [x] React 19 frontend with Vite and MUI
* [x] Comprehensive test suite (pytest + Jest)
* [x] Test coverage reporting
* [x] AI suggestion generation (Sonar AI)
* [x] Route optimization (OpenRouteService)
* [x] Weather integration (Open-Meteo)
* [x] Sphinx documentation
* [x] Docker and Docker Compose setup
* [x] Render deployment
* [x] Database migrations (Alembic)
* [x] Internationalization (i18n)
* [x] Code quality tools (Pylint, ESLint)
* [x] AWS EC2 Deployment with DuckDNS and Let's Encrypt (HTTPS)
* [x] GitHub Actions CI/CD pipelines
* [x] Docker Compose for local development
---

## 🤝 Contributing

    Contributions are allways welcome! Especially in the frontend, my proficiency with React is limited and suggestions are welcome.
    Please fork the repo, create a feature branch, and submit a pull request to dev. Use conventional commit messages and make sure all tests pass.

---

## 🪪 License

This project is licensed under the Attribution-NonCommercial 4.0 International License.