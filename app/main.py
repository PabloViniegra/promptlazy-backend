from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api import prompt

app = FastAPI(title="PromptLazy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prompt.router)


@app.get("/")
def read_root():
    """
    Root endpoint.
    Returns a welcome message for the PromptLazy API.
    """
    return {"message": "Welcome to the PromptLazy API!"}


@app.options("/")
def api_options():
    """
    OPTIONS endpoint for '/'.
    Returns the available HTTP methods and endpoints of the API.
    """
    return {
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "endpoints": ["/", "/auth", "/prompt"],
    }


@app.get("/status")
def api_status():
    """
    Status endpoint.
    Returns a message indicating that the API is alive and running.
    """
    return {"status": "alive", "message": "La API está viva y coleando!"}
