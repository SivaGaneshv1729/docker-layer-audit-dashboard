# Docker Image Optimization Analyzer

A comprehensive tool for analyzing Docker image layers and optimizing build cache performance. This project includes a Python-based analyzer (CLI & API) and a web-based dashboard for visualization.

## Project Structure

- `analyzer_tool/`: Python CLI and FastAPI server for image analysis and Dockerfile linting.
- `dashboard/`: Web-based dashboard for visualizing analysis reports.
- `apps/`: Benchmark applications (Go, Node.js, Python) with optimized Dockerfiles.
- `docker-compose.yml`: Orchestration for the entire system.

## Setup & Usage

1. **Clone the repository.**
2. **Copy `.env.example` to `.env`** and adjust settings if necessary.
3. **Run the system**:
   ```bash
   docker-compose up --build
   ```
4. **Access the Dashboard**: Open `http://localhost:3000` in your browser.
5. **Access the API**: The backend is available at `http://localhost:8000`.

## Features

- **Deep Image Inspection**: Detailed breakdown of layer sizes and creation commands.
- **Static Linting**: Identify Dockerfile anti-patterns (e.g., using `ADD` instead of `COPY`).
- **Optimization Benchmark**: Track and visualize size reductions across different build versions.
- **Multi-Framework Support**: Optimization examples for Go, Node.js, and Python.
