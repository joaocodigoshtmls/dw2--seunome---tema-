from fastapi import FastAPI
from .database import engine

app = FastAPI(title='VENDAS - Backend')


@app.get('/health')
def health():
    return {"status": "ok"}
