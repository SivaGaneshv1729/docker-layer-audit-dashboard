# 🐳 Docker Image Optimization Analyzer

A professional, end-to-end DevOps suite designed to analyze Docker image layers, lint Dockerfiles for security/performance anti-patterns, and visualize optimization opportunities through a modern React dashboard.

## 🚀 Key Features

*   **Deep Image Inspection**: Communicates directly with the host's Docker Daemon to break down your images layer-by-layer, identifying exactly which `RUN`, `COPY`, or `ADD` commands are bloating your image.
*   **Static Dockerfile Linting**: Automatically detects anti-patterns (e.g., failing to clean up `apt-get` caches, running as `root`, using the `ADD` instruction improperly).
*   **Visual Dashboard**: A beautiful, premium React frontend utilizing Vite and Chart.js to provide clear visual profiling of container assets.
*   **Polyglot Benchmarks**: Includes real-world optimization benchmarks for **Go**, **Node.js**, and **Python**.

## 📊 Proven Optimization Results

The repository includes a set of benchmark applications demonstrating the path from a naive build (`Dockerfile.v1`) to an ultra-optimized production build (`Dockerfile.v3`/`v4`).

*   🟢 **Go Microservice**: **1.54 GB ➔ 18.4 MB (98% Reduction)**
    *   *Techniques*: Multi-stage builds, compiling static binaries (`CGO_ENABLED=0`), and deploying onto `scratch` or `distroless` base images.
*   🟡 **Node.js App**: **1.09 GB ➔ 186 MB (83% Reduction)**
    *   *Techniques*: Using `node:18-alpine`, cleaning npm caches (`npm ci`), dropping `devDependencies`, and running as a non-root user.
*   🔵 **Python ML App**: **1.99 GB ➔ 828 MB (58% Reduction)**
    *   *Techniques*: Leveraging `python:3.11-slim-bookworm`, compiling wheels in a builder stage, avoiding `python3-dev`/`gcc` in the final image, and disabling bytecode (`PYTHONDONTWRITEBYTECODE=1`).

## 🏗️ Architecture

1.  **Backend (Analyzer Tool)**: Built with Python, **FastAPI**, and the **Docker SDK**. It mounts `/var/run/docker.sock` to dynamically inspect local images.
2.  **Frontend (Dashboard)**: Built with **React.js** and **Vite**. Features interactive charts to quickly spot heavy image layers.
3.  **Orchestration**: Managed entirely via **Docker Compose** for a seamless, one-click startup.

## 🛠️ Setup & Installation

**Prerequisites:** You must have Docker and Docker Compose installed on your system.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SivaGaneshv1729/docker-layer-audit-dashboard.git
    cd docker-layer-audit-dashboard
    ```
2.  **Start the Suite**:
    ```bash
    docker-compose up -d --build
    ```
3.  **Access the Dashboard**:
    Open your browser and navigate to `http://localhost:3000`.

## 🎮 How to Use

1.  **Build a Benchmark Image**:
    To see the analyzer in action, build one of the test applications locally:
    ```bash
    docker build -f apps/go-app/Dockerfile.v1 -t go-app:v1 ./apps/go-app
    docker build -f apps/go-app/Dockerfile.v3 -t go-app:v3 ./apps/go-app
    ```
2.  **Analyze**: Type `go-app:v1` into the Dashboard's **Analyze Image** input field to see its massive layer footprint, then compare it with `go-app:v3`.
3.  **Lint**: Paste the contents of `apps/python-app/Dockerfile.v1` into the Dashboard's **Lint Dockerfile** text area to see real-time security and cache warnings.
