# Docker SaaS Manager

## Project Description
This is a Python-based web application (SaaS) that provides a user interface to manage Docker containers.
It allows users to Create, Start, Stop, and Delete Nginx containers.
Each created container serves a **custom index.html** page, demonstrating Docker volume mounting capabilities.

**Target Environment:** Linux VM (Ubuntu/Rocky/Debian).

## ⚠️ IMPORTANT CONSTRAINTS
- **Linux ONLY**: This project is designed to run on a Linux Virtual Machine.
- **No Docker Desktop**: Do not try to run this with Docker Desktop on Windows/Mac. It expects a native Linux Docker socket.
- **Python Control**: All Docker operations are handled via the Python Docker SDK.

---

## Installation Steps (Linux VM)

### 1. Prerequisites
Ensure you have `python3`, `pip`, and `docker` installed on your Linux VM.

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip docker.io
# docker-saas

This repository is a small example Flask application that demonstrates a minimal "docker-backed" SaaS-like workflow: a web UI that lists and controls Docker containers, plus an API that can create an Nginx container which serves a custom `index.html` from the project.

The app is intentionally simple and educational — it shows how to:
- Use the Docker Engine API from Python to list, start, stop, and remove containers.
- Mount host files into containers (the project provides a custom `nginx/index.html`).
- Serve a basic web UI (Flask templates + static assets) which consumes the API.

Files of interest:
- `app.py`: Flask application and Docker integrations (API + web routes).
- `requirements.txt`: Python dependencies (`Flask`, `docker`).
- `nginx/index.html`: Custom HTML file that will be mounted into created Nginx containers.
- `templates/index.html`: Web UI template served at `/`.
- `static/`: JavaScript/CSS used by the UI.

**Objectives**
- **Educational goal:** Provide a compact, hands-on example that demonstrates how to control Docker from Python and build a minimal web UI to manage containers.
- **Practical goal:** Let users create lightweight Nginx containers that serve a custom HTML file from the host, and practice container lifecycle operations (create/start/stop/delete) via a REST API.
- **Security awareness goal:** Show why mounting host files and exposing Docker control requires care; document best practices for development vs. production.

**Main code sections (critical roles)**
Below are the core code locations and their responsibilities so you can quickly find and modify behavior.

- `app.py` (critical)
   - Docker client initialization:
      - `client = docker.from_env()` — creates the Docker SDK client using the host environment (Docker socket). Errors here mean Docker isn't available or accessible.
   - Route `index()`:
      - Serves the web UI from `templates/index.html`.
   - Route `list_containers()` (`GET /api/containers`):
      - Lists all containers (`client.containers.list(all=True)`), extracts short id, name, status, image tag, and port mapping for `80/tcp` if present.
      - Returns JSON list to the UI.
   - Route `create_container()` (`POST /api/containers`):
      - Reads optional `name` from the JSON body.
      - Resolves `nginx/index.html` on disk and mounts it into the container at `/usr/share/nginx/html/index.html` (read-only).
      - Runs `nginx:latest` with `ports={'80/tcp': None}` to bind to a random host port.
      - Handles common Docker errors: `ImageNotFound`, API errors, and filesystem-missing errors.
   - Route `container_action(container_id)` (`POST /api/containers/<id>/action`):
      - Accepts `action` in JSON: `start`, `stop`, `delete`.
      - Uses `client.containers.get(container_id)` and then calls `start()`, `stop()`, or `remove(force=True)` accordingly.
   - `if __name__ == '__main__'`:
      - Starts Flask with `app.run(host='0.0.0.0', port=5000, debug=True)` for development.

- `templates/index.html` (UI)
   - The single-page template that includes the frontend script and placeholders used by `static/script.js` to render the container list and action buttons.

- `static/script.js` (UI logic)
   - Calls the API endpoints to list containers, create containers, and invoke start/stop/delete actions.
   - Updates the DOM dynamically; this is the glue between the user and the Flask API.

- `nginx/index.html` (mounted into created containers)
   - Simple static HTML used to demonstrate mounting host files into containers. This file is what will be visible when you open the container's mapped port in a browser.

If you plan to extend the project, these are the main places to modify behavior:
- Change the container image or mount path in `create_container()` to use other images.
- Add authentication or CSRF protection to the Flask routes before exposing the app to untrusted networks.
- Improve port mapping control to allow fixed ports instead of ephemeral ports.

**Note:** This repo assumes you have Docker running on the host where the Flask app runs, because the app talks to the Docker daemon via the local Docker socket.

**Important security note:** Mounting host files into containers and exposing Docker API access should only be done in trusted environments. Do not expose this application to untrusted networks without proper authentication and isolation.

**Supported platform / prerequisites**
- Windows 10/11 (Docker Desktop with WSL2 backend recommended) or Linux/macOS with Docker Engine.
- Python 3.8+ (3.10+ recommended).
- Docker Desktop or Docker Engine running locally and accessible to the user running the Flask app.

**High-level behavior**
- GET `/` — serves the web UI from `templates/index.html`.
- GET `/api/containers` — returns a JSON list of containers (running and stopped).
- POST `/api/containers` — creates and starts a new `nginx:latest` container that serves the project `nginx/index.html` file. Request body: JSON with optional `name`.
- POST `/api/containers/<container_id>/action` — perform `start`, `stop`, or `delete` on a container. Request body: JSON with `action`.

---

**Getting started (PowerShell)**

1) Clone the repo (if you haven't already):

```powershell
git clone <repo-url>
Set-Location docker-saas
```

2) Install Python dependencies inside a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Start Docker Desktop / Docker Engine and ensure your user can access Docker.
   - On Windows, start Docker Desktop and ensure it shows "Docker is running".
   - If Docker complains about permissions, run Docker Desktop as your user or enable WSL2 integration.

4) Run the Flask app (development mode):

```powershell
python app.py
```

The app listens on port `5000` by default and binds to `0.0.0.0` so it is reachable from other machines on the host. Open `http://localhost:5000/` in your browser to view the UI.

---

**API: Examples**

List containers (from PowerShell using `curl` alias which maps to `Invoke-WebRequest`):

```powershell
# Using curl (if available) or PowerShell Invoke-RestMethod
curl http://localhost:5000/api/containers
# or
Invoke-RestMethod -Uri http://localhost:5000/api/containers -Method Get
```

Create an Nginx container that serves the project's `nginx/index.html`:

```powershell
# JSON body must include at least {} or {"name":"my-nginx"}
Invoke-RestMethod -Uri http://localhost:5000/api/containers -Method Post -ContentType 'application/json' -Body (@{name='my-nginx'} | ConvertTo-Json)
```

The endpoint will attempt to mount `./nginx/index.html` into the container at `/usr/share/nginx/html/index.html` and bind container port 80 to a random host port. If the file is missing, the API returns an error explaining the expected path.

Start / stop / delete a container by short id (example using PowerShell):

```powershell
# Perform action: start | stop | delete
Invoke-RestMethod -Uri http://localhost:5000/api/containers/<container_id>/action -Method Post -ContentType 'application/json' -Body (@{action='stop'} | ConvertTo-Json)
```

---

**How the container mount works**
- The code uses the absolute path to `nginx/index.html` in the project directory and mounts it read-only into the running `nginx:latest` container at `/usr/share/nginx/html/index.html`.
- Because the Flask app tells Docker to bind container port 80 to an ephemeral host port, you must inspect the container (or the API's returned data) to find which host port was chosen if you want to browse the Nginx site directly.

Example: after creating a container, run `docker ps` (locally) to see the mapped port, or request the `/api/containers` endpoint which returns a `port` field when the mapping exists.

---

**Running the project in Docker (optional)**

This repo does not include a Dockerfile for the Flask application. If you want to run the Flask app inside a container, create a simple Dockerfile, then run it and make sure you mount the Docker socket so the Flask container can control Docker on the host (this has security implications).

Example Dockerfile (not included in this repo — create it if you want):

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

Run (instructive example showing socket mount — do NOT use in untrusted environments):

```powershell
docker build -t docker-saas:latest .
docker run -it --rm -p 5000:5000 -v //var/run/docker.sock:/var/run/docker.sock -v ${PWD}:/app docker-saas:latest
```

On Windows with Docker Desktop, the Docker socket path differs; consult Docker Desktop docs for mounting the engine into a Linux container. The guidance above is primarily for Linux hosts.

---

**Troubleshooting**
- Error connecting to Docker: Ensure Docker Desktop / Engine is running and the Flask process has access to the Docker socket.
- `ImageNotFound` when creating containers: The app will return a helpful message; you can manually run `docker pull nginx:latest` to prefetch the image.
- Missing `nginx/index.html`: The create endpoint checks and will return a 400 with the absolute path it's expecting. Ensure the file exists and is readable.

If you want me to, I can:
- Add a `Dockerfile` and `docker-compose.yml` to run the app and Docker-in-Docker (or socket mount) for development.
- Add simple tests for the API endpoints.

---

**License & attribution**
This repository is provided as-is for learning and demonstration purposes. Review and adapt the code before using it in production.
