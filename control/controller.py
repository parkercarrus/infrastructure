from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import threading
import time

# Import your strategy module
import strategy

app = FastAPI()

def controller_loop():
    while True:
        current_time = datetime.now()
        result = strategy.get_current_trading_decision(['AAPL', 'MSFT'])
        print(f"Sample Strategy Result at {current_time}: {result}")
        time.sleep(1)

@app.get("/start-controller/")
def start_controller():
    thread = threading.Thread(target=controller_loop, daemon=True)
    thread.start()
    return JSONResponse(content={"status": "Controller started"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
