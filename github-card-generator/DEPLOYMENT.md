# Deployment Guide: GitHub Dev Card Generator to Google Cloud Run

This guide explains how to deploy your **GitHub Dev Card Generator** to Google Cloud Run.

## Prerequisites
1.  **Google Cloud Project:** Created and billed.
2.  **gcloud CLI:** Installed and authenticated (`gcloud auth login`).
3.  **Docker:** Running locally.

---

## Step 1: Deploy the Backend
The backend is an agentic FastAPI service.

1.  **Navigate to the backend folder:**
    ```bash
    cd backend
    ```

2.  **Build and Push the image to Google Artifact Registry:**
    *(Replace `PROJECT_ID` with your actual GCP Project ID)*
    ```bash
    gcloud builds submit --tag gcr.io/PROJECT_ID/github-card-backend
    ```

3.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy github-card-backend \
      --image gcr.io/PROJECT_ID/github-card-backend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars="GOOGLE_API_KEY=YOUR_KEY,GITHUB_TOKEN=YOUR_TOKEN"
    ```
    *   **Note the URL** provided after deployment (e.g., `https://github-card-backend-xyz.a.run.app`).

---

## Step 2: Deploy the Frontend
The frontend is a React/Nginx app that needs to know the Backend URL.

1.  **Navigate to the frontend folder:**
    ```bash
    cd ../frontend
    ```

2.  **Build and Push the image:**
    ```bash
    gcloud builds submit --tag gcr.io/PROJECT_ID/github-card-frontend
    ```

3.  **Deploy to Cloud Run:**
    *Use the Backend URL you copied in Step 1 for the `BACKEND_URL` variable.*
    ```bash
    gcloud run deploy github-card-frontend \
      --image gcr.io/PROJECT_ID/github-card-frontend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars="BACKEND_URL=https://github-card-backend-xyz.a.run.app"
    ```

---

## Step 3: Persistence (Optional but Recommended)
Cloud Run is stateless. To keep generated cards permanent, you should:
1.  Create a **Google Cloud Storage (GCS)** bucket.
2.  Mount the bucket to the `/app/static/cards` path in the Backend Cloud Run service using **Cloud Storage FUSE**.

---

## Summary
Once Step 2 is complete, your app will be live at the Frontend service URL!
