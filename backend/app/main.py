from fastapi import FastAPI

app = FastAPI(title="InsightSwarm API")

@app.get("/")
def read_root():
    return {"message": "InsightSwarm backend is ready"}
