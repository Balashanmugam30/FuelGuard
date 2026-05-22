# FuelGuard AI

**AI-Powered Petrol Fraud Detection & Fuel Verification System**

FuelGuard AI is a software-based prototype that detects possible petrol underfilling scams at petrol bunks. It simulates fuel delivery transactions and verifies whether the requested petrol quantity matches the delivered quantity using mock data and intelligent fraud detection algorithms.

> **Note:** This is a software prototype. All fuel measurements are simulated — no hardware, IoT devices, or real sensors are used.

---

## Features

- **Fuel Transaction Simulation** — Generate mock fuel delivery data with a single click.
- **Fraud Detection Engine** — Automatically detect underfilling based on configurable thresholds.
- **Risk Assessment** — Classify transactions as Low, Medium, or High risk with numeric scores.
- **Analytics Dashboard** — Real-time aggregate statistics (fraud %, average shortage, etc.).
- **Interactive Charts** — Fraud vs Safe doughnut chart and shortage trend line chart (Chart.js).
- **Transaction Monitoring** — Searchable, filterable table of all transactions.
- **PDF Report Generation** — Download professional PDF reports with analytics and transaction details.
- **JSON Export** — Export all transaction data as a JSON file.
- **Responsive Design** — Works on desktop, tablet, and mobile.
- **Vercel Deployment** — Single-command deploy; frontend and backend in one project.

---

## Tech Stack

| Layer     | Technology                     |
| --------- | ------------------------------ |
| Frontend  | HTML, CSS, Vanilla JavaScript  |
| Backend   | Python, FastAPI                |
| Charts    | Chart.js 4                     |
| PDF       | ReportLab                      |
| Storage   | In-memory (Python lists)       |
| Hosting   | Vercel (Serverless)            |

---

## Folder Structure

```
FuelGuard AI/
│
├── api/
│   ├── index.py               # FastAPI server & routes (Vercel entry point)
│   ├── fraud_engine.py        # Fraud detection logic
│   ├── transaction_store.py   # In-memory transaction storage
│   └── report_generator.py    # PDF report generation
│
├── frontend/
│   ├── index.html             # Dashboard UI
│   ├── style.css              # Stylesheet
│   └── script.js              # Frontend logic
│
├── reports/                   # Generated PDF reports (local only)
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel deployment configuration
└── README.md                  # This file
```

---

## Running Locally

### Prerequisites

- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/))
- A modern web browser (Chrome, Edge, Firefox, Safari)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
uvicorn api.index:app --reload --port 8000
```

The API will be available at **http://localhost:8000**.

### 3. Open the Frontend

Since the frontend uses relative API paths (`/api/*`), there are two options:

**Option A — Use a simple HTTP server (recommended):**

```bash
# Serves files and proxies API calls
npx vercel dev
```

**Option B — Open the HTML file directly:**

Edit `frontend/script.js` and temporarily change `API_BASE` to:

```js
const API_BASE = "http://localhost:8000";
```

Then open `frontend/index.html` in your browser.

---

## Deploying to Vercel

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — FuelGuard AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fuelguard-ai.git
git push -u origin main
```

### 2. Import to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in.
2. Click **"Add New Project"**.
3. Import your GitHub repository.
4. Vercel will auto-detect the `vercel.json` configuration.
5. Click **Deploy**.

That's it — your app will be live at `https://your-project.vercel.app`.

### How It Works on Vercel

| Request          | Handled By                      |
| ---------------- | ------------------------------- |
| `/`              | `frontend/index.html`           |
| `/style.css`     | `frontend/style.css`            |
| `/script.js`     | `frontend/script.js`            |
| `/api/*`         | FastAPI serverless function      |

---

## API Documentation

### `GET /api/status`

Health check endpoint.

**Response:**
```json
{ "status": "FuelGuard AI Backend Running" }
```

---

### `POST /api/simulate-transaction`

Simulate a fuel delivery transaction.

**Request Body:**
```json
{ "requested_fuel": 5.0 }
```

**Response:**
```json
{
  "transaction_id": 1,
  "requested_fuel": 5.0,
  "delivered_fuel": 4.72,
  "difference": 0.28,
  "shortage_percentage": 5.6,
  "fraud_detected": true,
  "risk_level": "Medium",
  "risk_score": 54,
  "timestamp": "2026-05-22 12:30:00"
}
```

---

### `GET /api/transactions`

Returns all stored transactions (newest first).

---

### `GET /api/analytics`

Returns aggregate analytics.

**Response:**
```json
{
  "total_transactions": 10,
  "fraud_transactions": 7,
  "safe_transactions": 3,
  "fraud_percentage": 70.0,
  "average_shortage": 5.43,
  "highest_shortage": 12.5
}
```

---

### `GET /api/export-json`

Download all transactions as a JSON file.

---

### `GET /api/generate-report`

Generate and download a professional PDF report.

---

## Fraud Detection Logic

| Shortage (L)   | Risk Level | Risk Score | Fraud Detected |
| -------------- | ---------- | ---------- | -------------- |
| 0 – 0.03      | Low        | 0 – 30     | No             |
| 0.03 – 0.07   | Medium     | 31 – 70    | Yes            |
| Above 0.07    | High       | 71 – 100   | Yes            |

---

## Screenshots

> _Screenshots will be added here._

| View                  | Screenshot                |
| --------------------- | ------------------------- |
| Dashboard             | _(placeholder)_           |
| Simulation Result     | _(placeholder)_           |
| Analytics             | _(placeholder)_           |
| Charts                | _(placeholder)_           |
| Transaction Table     | _(placeholder)_           |
| PDF Report            | _(placeholder)_           |

---

## Notes

- **Serverless storage:** On Vercel, in-memory data resets on cold starts. This is expected for a prototype. For production, add a database.
- **PDF reports:** On Vercel, reports are written to `/tmp` (ephemeral). They are streamed directly to the browser as downloads.

---

## License

This project is a software prototype built for educational and demonstration purposes.

---

**Built with ❤️ by FuelGuard AI Team**
