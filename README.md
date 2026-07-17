# AI-Powered Civic Issue Reporting System

React/Vite frontend and Django backend for reporting civic issues with image upload, duplicate detection, department dashboards, status tracking, and TensorFlow-based image classification.

## Local development

Backend:

```bash
cd civicbackend
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd civic_frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` for the frontend when the backend is not running at `http://127.0.0.1:8000`.

## Render

The repository includes `render.yaml` for a Django web service, Vite static site, and Render Postgres database. Required runtime versions are pinned with `.python-version`, `runtime.txt`, and `civic_frontend/.node-version`.
