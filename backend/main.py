from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}