# Planorama

Planorama is a smart travel planning backend powered by FastAPI and AI. It integrates user-generated itineraries, location data, weather, and route optimization into a seamless travel planning API.

> ⚠️ This project is under active development. Expect breaking changes until v1.0 is released.

---

## 🚀 Tech Stack

| Layer          | Tech                            |
|----------------|---------------------------------|
| Backend        | FastAPI, SQLAlchemy, Pydantic   |
| Frontend       | React, GUI                      |
| Database       | PostgreSQL, Alembic             |
| Auth           | JWT (manual), Auth0 (WIP)       |
| AI Services    | OpenAI, OpenRoute, Weather APIs |
| DevOps         | Docker, Render, .env configs    |
| Testing        | Pytest, pre-commit, Pylint      |
| Docs (Planned) | Sphinx, Markdown                |

---

## 📁 Project Structure (In Progress)

<details>
<summary>Click to expand</summary>
<br>
> 📁 Folders like `activities`, `auth`, `travel`, etc. follow a **feature module pattern**, each containing `api.py`, `models.py`, `schemas.py`, and `services.py` for separation of concerns.
<br>
<br>
project_root/<br>
├── app/<br>
│   ├── activities/<br>
│   │   ├── api.py<br>
│   │   ├── models.py<br>
│   │   ├── schemas.py<br>
│   │   └── services.py<br>
│   ├── auth/  # Feature module (api/models/schemas/services)<br>
│   │   └── ...<br>
│   ├── core/<br>
│   │   ├── config.py, database.py, security.py, ...<br>
│   ├── custom_docs/  # Custom OpenAPI docs logic<br>
│   │   └── api.py, services.py<br>
│   ├── external_services/<br>
│   │   ├── chatgpt.py, weather_api.py, ...<br>
│   │   └── connectors/<br>
│   │       └── openroute_connector.py<br>
│   ├── quotes/        # Feature module<br>
│   │   └── ...<br>
│   ├── stations/      # Feature module<br>
│   │   └── ...<br>
│   ├── travel/        # Feature module<br>
│   │   └── ...<br>
│   ├── trips/         # Feature module<br>
│   │   └── ...<br>
│   ├── users/         # Feature module<br>
│   │   └── ...<br>
│   ├── static/<br>
│   ├── templates/<br>
│   ├── utils/<br>
│   ├── __init__.py<br>
│   └── main.py<br>
├── docker/<br>
│   ├── development/<br>
│   ├── postgres/<br>
│   └── production/<br>
├── frontend/<br>
├── migrations/<br>
│   ├── versions/<br>
│   ├── env.py<br>
│   ├── README<br>
│   └── script.py.mako<br>
├── tests/<br>
│   ├── test_auth.py<br>
│   └── test_trip.py<br>
├── .env / .env.example<br>
├── .gitignore<br>
├── .pylintrc<br>
├── alembic.ini<br>
├── LICENSE<br>
├── pre-commit-config.yaml<br>
├── pyproject.toml<br>
├── README.md<br>
└── requirements.txt<br>

</details>

<br>

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

## 📌 Roadmap

* [x] FastAPI scaffolding

* [x] SQLAlchemy models

* [x] JWT authentication

* [x] Auth0 integration

* [ ] React MUI frontend

* [ ] Pytest coverage

* [ ] AI route generation

* [ ] Sphinx docs

* [ ] Render deployment

* [ ] Dockerization

## 🤝 Contributing

    Contributions are welcome once the groundwork is done!
    Please fork the repo, create a feature branch, and submit a pull request to dev. Use conventional commit messages and make sure all tests pass.

## 🪪 License

This project is licensed under the MIT License.