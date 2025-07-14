from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limiter import limiter
from app.api import auth
from app.api import prompt

app = FastAPI(title="PromptLazy API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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
def read_root(request: Request):
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
def api_status(request: Request):
    """
    Status endpoint.
    Returns a message indicating that the API is alive and running.
    """
    return {"status": "alive", "message": "La API está viva y coleando!"}
