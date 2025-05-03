# 🐍 Stacksync Challenge

This project provides a secure API service that allows users to execute arbitrary Python scripts inside a sandboxed environment using [nsjail](https://nsjail.dev/) and [Flask](https://flask.palletsprojects.com/). It ensures isolation and safety against malicious code execution attempts.

---

## 🚀 Features

- Accepts Python scripts via a POST request to `/execute`
- Returns the output of `main()` and any printed output separately
- Secure execution with `nsjail` (CPU, memory, and filesystem constraints)
- Basic Python packages like `os`, `numpy`, `pandas`, etc. are available
- Input validation to ensure only valid scripts with a `main()` function are executed
- Lightweight Docker container

---

## 📦 Tech Stack

- Python 3.10
- Flask
- nsjail
- Docker
- Google Cloud Run (for deployment)

---

## 📥 Local Setup (Docker)

### 1. Build the Docker image:
```bash
docker build -t stacksync-challenge .
```

### 2. Run the container:
```bash
docker run -d -p 8080:8080 --name stacksync-service --privileged stacksync-challenge
```

> 🔐 **Note**: `--privileged` is required for proper nsjail operation.

---

## 🔁 Example API Usage

### GCE Endpoint:
```
POST http://34.72.72.150:8080/execute
```

### Cloud Run Endpoint:
```
POST https://stacksync18-208739245329.us-central1.run.app/execute 
```

### Request Body:
```json
{
  "script": "def main():\n    return {'message': 'Hello from sandbox!'}"
}
```

### Example curl Command (GCE):
```bash
curl -X POST http://34.72.72.150:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"message\": \"Hello from sandbox!\"}"}'
```

### Example curl Command (Cloud Run):
```bash
curl -X POST https://stacksync18-208739245329.us-central1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"message\": \"Hello from sandbox!\"}"}'
```

### Example Response:
```json
{
  "result": {
    "message": "Hello from sandbox!"
  },
  "stdout": ""
}
```

---

## ✅ Requirements & Safety

- The script must define a `main()` function.
- The `main()` function must return a JSON-serializable object.
- Any print statements are captured and returned separately.
- All execution is sandboxed using nsjail, preventing:
  - File system writes outside `/tmp`
  - Network access
  - Import of restricted modules
  - CPU/memory/disk abuse

---

## 🕒 Time Estimate

This project took approximately **5 hours** to research, implement, test, and containerize securely.

---

