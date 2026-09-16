from fastapi import FastAPI
from os import getenv
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from airpas.lib.exceptions import attach_exception_handlers
from airpas.lib.util_schemas import HttpStatusSchema
from airpas.config.storage import LOCAL_STORAGE_DIR, LOCAL_STORAGE_URL_PREFIX
from airpas.routes import user_router, receipt_router, receipt_line_router, file_router
from datetime import datetime
# CORS Origins can be loaded from environment
CORS_ORIGINS = getenv("CORS_ORIGINS", "").split(",")
[CORS_ORIGINS.append(origin) for origin in getenv("ADMIN_CORS_ORIGIN", "").split(",")]

app_options = {
  "title": "Airpas",
  "description": "API for Airpas application",
  "version": "1.0.0",
  "openapi_tags": [
          {"name": "Users", "description": "User list and manipulation operations."},
          {"name": "Receipts", "description": "Receipt list and manipulation operations."},
          {"name": "Receipt Lines", "description": "Receipt line list and manipulation operations."},
          {"name": "Files", "description": "Receipt file list and manipulation operations."},
          {"name": "Utility", "description": "Application and monitoring utilities."},
      ],
  }

app = FastAPI(**app_options)
if len(CORS_ORIGINS) > 0:
  app.add_middleware(
      CORSMiddleware,
      allow_origins=CORS_ORIGINS,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
      expose_headers=["*", "Authorization"],
  )

attach_exception_handlers(app)

# Initialize sub-routers for each domain:
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(receipt_router, prefix="/api/receipts", tags=["Receipts"])
app.include_router(receipt_line_router, prefix="/api/receipts/{receipt_id}/lines", tags=["Receipt Lines"])
app.include_router(file_router, prefix="/api/receipts/{receipt_id}/files", tags=["Files"])

@app.get("/api/status", tags=["Utility"], response_model=HttpStatusSchema)
def status():
    """
    Endpoint to check if the API is running and healthy.
    """
    return HttpStatusSchema(ok=True, ts=datetime.now(), message="API is running and healthy.")

app.mount(LOCAL_STORAGE_URL_PREFIX, StaticFiles(directory=LOCAL_STORAGE_DIR), name="local")
app.mount("/", StaticFiles(directory="airpas/static", html=True), name="static")
