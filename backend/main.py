# backend/main.py
import os
from fastapi import FastAPI
from .db import engine, Base
from .models import Email, Event
from .routes import ai_routes, event_routes, email_routes
from .routes import contact_routes  # ✅ Import contact routes
from .scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# create DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Email & Calendar Automation MVP")

# Add this BEFORE your routers
# origins = [
#     "http://localhost:5173",  # frontend URL
#     "http://127.0.0.1:5173",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] to allow all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(ai_routes.router)
app.include_router(event_routes.router)
app.include_router(email_routes.router)
app.include_router(contact_routes.router)  # ✅ Include contact routes


@app.on_event("startup")
def startup_event():
    # start scheduler
    try:
        start_scheduler()
    except Exception as e:
        print("Failed to start scheduler:", e)
