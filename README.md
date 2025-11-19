## Setup Instructions

1. **Initialize Frontend**

    ```bash
    cd frontend
    rm -rf node_modules && rm -rf package-lock.json && rm -rf .next && npm install
    npm run dev
    ```

2. **Initialize and Seed (for testing) Database**

    ```bash
    cd src
    python -m database.init_duckdb
    python -m database.seed_db
    ```

3. **Run the Controller**

    ```bash
    python -m controller.runController
    ```

3. **Run the BFF (Backend for Frontend)**

    ```bash
    cd src
    uvicorn bff:app --reload
    ```
    
Run all of these in separate terminals
Go to localhost:3000 to view frontend