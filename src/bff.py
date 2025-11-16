# bff = Backend for Frontend
import duckdb
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/trades")
def trades():
    con = duckdb.connect("algory.duckdb")
    df = con.execute("SELECT * FROM trades ORDER BY timestamp").df()
    return df.to_dict(orient="records")

@app.get("/portfolio")
def portfolio():
    con = duckdb.connect("algory.duckdb")
    df = con.execute("SELECT * FROM portfolio_history ORDER BY timestamp").df()
    return df.to_dict(orient="records")
