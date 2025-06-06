# Planorama

Planorama is a smart travel planning backend powered by FastAPI and AI. It integrates user-generated itineraries, location data, weather, and route optimization into a seamless travel planning API.

> ⚠️ This project is under active development. Expect breaking changes until v1.0 is released.

---

## 🚀 Tech Stack

| Layer         | Tech                            |
|---------------|----------------------------------|
| Backend       | FastAPI, SQLAlchemy, Pydantic    |
| Database      | PostgreSQL, Alembic              |
| Auth          | JWT (manual), Auth0 (WIP)        |
| AI Services   | OpenAI, OpenRoute, Weather APIs  |
| DevOps        | Docker, Render, .env configs     |
| Testing       | Pytest, pre-commit, Pylint       |
| Docs (Planned)| Sphinx, Markdown                 |

---

## 📁 Project Structure (In Progress)

<details> <summary>Click to expand</summary>
<br>
planorama/<br>
├── app/  <br>
│   ├── api/              # Route handlers (REST)<br>
│   ├── core/             # App-wide config, logging, auth<br>
│   ├── crud/             # DB access layer<br>
│   ├── db/               # DB session, base, handlers<br>
│   ├── models/           # SQLAlchemy models<br>
│   ├── pages/            # Route handlers (HTML)<br>
│   ├── schemas/          # Pydantic schemas<br>
│   ├── services/         # External APIs, AI integration<br>
│   ├── static/           # Assets<br>
│   ├── templates/        # Jinja2 templates (if needed)<br>
│   ├── utils/            # MCP client/server setup<br>
│   └── main.py           # Entrypoint (FastAPI app)<br>
├── docker/<br>
├── alembic/<br>
├── .env / .env.example<br>
├── requirements.txt<br>
├── README.md<br>
└── LICENSE<br>
</details>

<br>

## 🔧 Setup (Development)

```bash
# Clone the repo
git clone https://github.com/your-username/planorama.git
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
```

## 📌 Roadmap

* [ ] FastAPI scaffolding

* [ ] SQLAlchemy models

* [ ] JWT authentication

* [ ] Auth0 integration

* [ ] Dockerization

* [ ] Pytest coverage

* [ ] AI route generation

* [ ] Sphinx docs

* [ ] Render deployment

## 🤝 Contributing

    Contributions are welcome once the groundwork is done!
    Please fork the repo, create a feature branch, and submit a pull request to dev. Use conventional commit messages and make sure all tests pass.

## 🪪 License

This project is licensed under the MIT License.