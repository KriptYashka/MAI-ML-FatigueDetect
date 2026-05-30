from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import requests

app = FastAPI(
    title="Определение Усталости Пилотов",
    description="Система мониторинга усталости для авиации",
    version="1.0.0",
)

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "server_url": SERVER_URL})


@app.get("/client")
async def client(request: Request):
    return await home(request)


@app.get("/api/status")
async def get_status():
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        return {"connected": True, "server_status": response.json()}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        response = requests.post(f"{SERVER_URL}/predict/image", files=files, timeout=60)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/tabular")
async def upload_tabular(data: dict):
    try:
        response = requests.post(
            f"{SERVER_URL}/predict/tabular",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/batch/tabular")
async def upload_batch_tabular(data: list):
    try:
        response = requests.post(
            f"{SERVER_URL}/predict/batch/tabular",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
