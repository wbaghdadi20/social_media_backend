from fastapi import FastAPI
import socket

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/instance")
def get_instance():
    hostname = socket.gethostname()
    return {"instance": hostname}