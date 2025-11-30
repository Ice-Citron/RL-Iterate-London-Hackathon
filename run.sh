#!/bin/bash
# Start the FastAPI CAI server on port 4000
uvicorn fastapi_cai_server:app --reload --host 0.0.0.0 --port 4000
