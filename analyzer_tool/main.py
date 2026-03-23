import json
import re

import docker
import typer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = typer.Typer()
api_app = FastAPI()


def get_docker_client():
    client = docker.from_env()
    client.ping()
    return client


def bytes_to_mb(size_bytes: int) -> float:
    return round(size_bytes / (1024 * 1024), 2)


def analyze_image_logic(image_name: str):
    try:
        client = get_docker_client()
        image = client.images.get(image_name)
    except docker.errors.DockerException as exc:
        return {"error": f"Could not connect to Docker daemon: {exc}"}
    except docker.errors.ImageNotFound:
        return {"error": f"Image '{image_name}' not found"}
    except Exception as exc:
        return {"error": str(exc)}

    history = image.history()
    layers = []
    for layer in history:
        layers.append({
            "Id": layer.get("Id", "unknown"),
            "CreatedBy": layer.get("CreatedBy", "unknown"),
            "Size": layer.get("Size", 0),
        })

    total_size = image.attrs.get("Size", 0)
    total_size_mb = bytes_to_mb(total_size)

    largest_layers = sorted(layers, key=lambda x: x["Size"], reverse=True)[:5]

    return {
        "image_id": image.id,
        "tags": image.tags,
        "total_size_mb": total_size_mb,
        "num_layers": len(layers),
        "layers": layers,
        "largest_layers": largest_layers,
    }


def lint_dockerfile_logic(content: str):
    warnings = []
    lines = content.split("\n")
    has_user = False

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith('#'):
            continue

        if re.search(r"^\s*ADD\s", stripped, re.IGNORECASE):
            warnings.append({
                "line": line_num,
                "severity": "warning",
                "message": "Use COPY instead of ADD for better cache control and security.",
            })

        lowered = stripped.lower()

        if "apt-get install" in lowered and "rm -rf /var/lib/apt/lists/*" not in stripped:
            warnings.append({
                "line": line_num,
                "severity": "error",
                "message": "Chain `apt-get install` with `rm -rf /var/lib/apt/lists/*` in the same RUN layer to reduce image size.",
            })

        if "apt-get install" in lowered and "--no-install-recommends" not in stripped:
            warnings.append({
                "line": line_num,
                "severity": "warning",
                "message": "Use --no-install-recommends to avoid installing unnecessary packages.",
            })

        if "pip install" in lowered and "--no-cache-dir" not in stripped:
            warnings.append({
                "line": line_num,
                "severity": "warning",
                "message": "Use `pip install --no-cache-dir` to prevent bloating the image with cache files.",
            })

        if re.search(r"^\s*COPY\s+\.\s+\.", stripped, re.IGNORECASE):
            warnings.append({
                "line": line_num,
                "severity": "warning",
                "message": "Copy dependency manifests first to improve layer cache reuse before copying the full source tree.",
            })

        if stripped.upper().startswith("USER "):
            has_user = True

    if not has_user:
        warnings.append({
            "line": 0,
            "severity": "error",
            "message": "Container is configured to run as root. Create and switch to a non-root user for security.",
        })

    return warnings


@app.command()
def analyze(image_name: str):
    """Analyze a Docker image and print a JSON report."""
    report = analyze_image_logic(image_name)
    print(json.dumps(report, indent=2))


@app.command()
def lint(dockerfile_path: str):
    """Lint a Dockerfile and print a JSON report."""
    try:
        with open(dockerfile_path, "r", encoding="utf-8") as f:
            content = f.read()
        warnings = lint_dockerfile_logic(content)
        print(json.dumps(warnings, indent=2))
    except Exception as exc:
        typer.echo(f"Error reading file {dockerfile_path}: {exc}", err=True)
        raise typer.Exit(code=1)


class LintRequest(BaseModel):
    dockerfile_content: str

class AnalyzeRequest(BaseModel):
    image_name: str


@api_app.get("/health")
def health_check():
    return {"status": "healthy"}


@api_app.post("/api/analyze")
async def analyze_image_endpoint(request: AnalyzeRequest):
    result = analyze_image_logic(request.image_name)
    if "error" in result:
        status_code = 404 if "not found" in result["error"].lower() else 503
        raise HTTPException(status_code=status_code, detail=result["error"])
    return result


@api_app.post("/api/lint")
async def lint_dockerfile_endpoint(request: LintRequest):
    return lint_dockerfile_logic(request.dockerfile_content)

if __name__ == "__main__":
    app()
