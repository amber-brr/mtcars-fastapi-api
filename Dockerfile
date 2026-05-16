# Dockerfile

# Python 3.11-slim image as base container image; smaller than full Python image
FROM python:3.11-slim 

# Sets /app as working dir in container
# -> COPY, RUN, CMD will run relative to /app
# -> inside container, project will live here 
WORKDIR /app

# Copies local requirements.txt into container's current working dir
# -> this means: local requirements.txt -> container /app/requirements.txt
# -> '.'' means “copy it here” meaning into /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# '--no-cache-dir' prevents pip from saving package cache files inside image
# -> helps keep the Docker/Podman image smaller

# Copies local app/ folder into container (local app/main.py -> /app/app/main.py)
# -> needed bc FastAPI app code is inside app/main.py
COPY app/ app/

# Copies local models/ folder into container (local models/model.pkl -> /app/models/model.pkl)
COPY models/ models/

# Documents that container listens on port 8080 (app expects to use port 8080)
EXPOSE 8080

# Command that starts FastAPI app when container runs
# -> 'uvicorn' starts Uvicorn web server 
# -> 'app.main:app' tells Uvicorn where to find FastAPI app
# --> means app.main = Python file app/main.py and app = FastAPI object inside that file
# -> '--host 0.0.0.0' makes API accessible from outside container
# -> '--port 8080' runs the API on port 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]