## Setup Instructions

1. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    cd frontend
    npm install
    ```

2. **Run the Controller**

    ```bash
    cd src
    python -m controller.runController
    ```

3. **Run the BFF (Backend for Frontend)**

    ```bash
    cd src
    uvicorn bff:app --reload
    ```

4. **Run the Frontend**

    ```bash
    cd frontend
    npm run dev
    ```

Go to localhost:3000 to view frontend