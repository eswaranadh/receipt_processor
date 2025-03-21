# Receipt Processor Service

A web service that processes receipts and calculates points based on defined rules.

## Output Preview

![image](https://github.com/user-attachments/assets/e62c8d2e-1cdd-4af1-bd85-301091c8f907)

![image](https://github.com/user-attachments/assets/4a3f78b0-dea4-4d82-8d9a-4ddcd0e6c454)


## Running the Application

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t receipt-processor .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 receipt-processor
   ```

## API Endpoints

### Process Receipt
- **POST** `/receipts/process`
- Processes a receipt and returns an ID
- Request body: Receipt JSON
- Response: `{ "id": "<receipt_id>" }`

### Get Points
- **GET** `/receipts/{id}/points`
- Returns points for a processed receipt
- Response: `{ "points": <points> }`
