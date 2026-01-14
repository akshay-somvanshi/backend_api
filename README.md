# Backend API

This repository contains a FastAPI-based backend API designed to provide services for managing sustainability-related data, documents, and user suggestions. It is built to integrate with Google Cloud services, leveraging BigQuery for data warehousing and Google Cloud Storage for document management.

## Features

*   **Dashboard API:** A set of endpoints for creating, retrieving, updating, and deleting sustainability-related actions, suppliers, and targets. It also allows for exploring dependencies between these entities.
*   **Knowledge API:** Provides functionality for uploading, listing, and deleting documents. It also supports the generation of secure, time-limited URLs for accessing documents, which is ideal for secure content delivery.
*   **Suggestions API:** A dedicated endpoint for fetching user-specific suggestions based on predefined criteria.
*   **Google Cloud Integration:** Natively integrates with:
    *   **Google BigQuery:** For storing and querying large-scale structured data related to actions, suppliers, and targets.
    *   **Google Cloud Storage:** For robust and scalable document and file storage.
*   **Containerized:** Comes with a `Dockerfile` for easy containerization, ensuring consistent deployments and scalability.
*   **API Versioning:** The API is versioned (`/api/v1/`) to ensure maintainability and backward compatibility.

## API Endpoints

All endpoints are available under the `/api/v1/` prefix. A `user_id` is required in the header for all requests.

### Dashboard API (`/api/v1/`)

*   `GET /action`: Fetches all actions for a user.
*   `DELETE /action/{action_id}`: Deletes a specific action.
*   `PUT /action/{action_id}`: Updates a specific action.
*   `GET /action/{action_id}/dependencies`: Retrieves actions that depend on a given action.
*   `GET /action/{action_id}/unlocks`: Retrieves actions that are unlocked by a given action.
*   `GET /supplier`: Fetches all suppliers for a user.
*   `GET /supplier/{supplier_id}/targets`: Fetches targets for a specific supplier.
*   `GET /target`: Fetches all targets for a user.

### Knowledge API (`/api/v1/`)

*   `GET /document`: Lists all documents for a user.
*   `POST /document`: Uploads a new document.
*   `GET /document/{document_path:path}/url`: Generates a secure, signed URL for a document.
*   `DELETE /document/{document_path:path}`: Deletes a specified document.

### Suggestions API (`/api/v1/`)

*   `GET /suggestions`: Retrieves suggestions for a user based on a `chip_type` query parameter.

## Getting Started

### Prerequisites

*   **Google Cloud Project:** With the following APIs enabled:
    *   BigQuery API
    *   Cloud Storage API
    *   Firebase (if used for authentication)
*   **Google Cloud SDK (`gcloud` CLI):** Installed and authenticated (`gcloud auth application-default login`).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/akshay-somvanshi/backend_api.git
    cd backend_api
    ```

2.  **Set up Environment Variables:**
    Create a `.env` file in the root of the project with your Google Cloud project details:

    ```ini
    GOOGLE_PROJECT_ID="your-gcp-project-id"
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

#### Locally (without Docker)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level debug
```
The API will be available at `http://localhost:8080`.

#### Using Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t backend-api .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8080:8080 --env-file ./.env backend-api
    ```
    The API will be available at `http://localhost:8080`.

## Project Structure

```
.
├── app/                  # Main application source code
│   ├── api/              # API endpoint definitions, versioned
│   │   └── v1/
│   │       ├── dashboard.py
│   │       ├── knowledge.py
│   │       └── suggestions.py
│   ├── core/             # Error handling
|   |    └── exceptions.py
│   ├── db/               # Database interaction logic (BigQuery, Storage)
│   ├── __init__.py
│   └── main.py           # FastAPI application entry point
├── cloudbuild.yaml       # Google Cloud Build configuration
├── Dockerfile            # Dockerfile for containerizing the application
├── README.md             # This README file
└── requirements.txt      # Python dependencies
```
