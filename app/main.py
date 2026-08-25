from fastapi import FastAPI

app = FastAPI(title="cloudtask")


@app.get("/health")
def health():
    return {"statue" : "OK"}
