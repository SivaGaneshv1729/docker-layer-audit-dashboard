import docker
import json
import typer
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import re
from typing import List, Optional

app = typer.Typer()
api_app = FastAPI()

# Initialize Docker client
def get_docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        print(f"Error connecting to Docker daemon: {e}")
        # In a real environment, we'd handle this more gracefully
        # For the tool, we want to know if it's not working
        return None

def analyze_image_logic(image_name: str):
    client = get_docker_client()
    if not client:
        return {"error": "Could not connect to Docker daemon"}
    
    try:
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        return {"error": f"Image '{image_name}' not found"}
    except Exception as e:
        return {"error": str(e)}

    history = image.history()
    # Filter out layers that are just tags
    layers = []
    for layer in history:
        layers.append({
            "Id": layer.get('Id', 'unknown'),
            "CreatedBy": layer.get('CreatedBy', 'unknown'),
            "Size": layer.get('Size', 0)
        })

    total_size = image.attrs['Size']
    total_size_mb = round(total_size / (1024 * 1024), 2)

    largest_layers = sorted(layers, key=lambda x: x['Size'], reverse=True)[:5]

    return {
        'image_id': image.id,
        'tags': image.tags,
        'total_size_mb': total_size_mb,
        'num_layers': len(layers),
        'layers': layers,
        'largest_layers': largest_layers
    }

def lint_dockerfile_logic(content: str):
    warnings = []
    lines = content.split('\n')
    
    has_user = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#'):
            continue

        # Rule 1: Use COPY instead of ADD
        if re.search(r'^\s*ADD\s', stripped, re.IGNORECASE):
            warnings.append({
                'line': line_num, 
                'severity': 'warning', 
                'message': 'Use COPY instead of ADD for better cache control and security.'
            })

        # Rule 2: apt-get cleanup
        if 'apt-get install' in stripped.lower() and 'rm -rf /var/lib/apt/lists/*' not in stripped:
            warnings.append({
                'line': line_num, 
                'severity': 'error', 
                'message': 'Chain `apt-get install` with `rm -rf /var/lib/apt/lists/*` in the same RUN layer to reduce image size.'
            })

        # Rule 3: Missing --no-install-recommends
        if 'apt-get install' in stripped.lower() and '--no-install-recommends' not in stripped:
            warnings.append({
                'line': line_num, 
                'severity': 'warning', 
                'message': 'Use --no-install-recommends to avoid installing unnecessary packages.'
            })
            
        # Rule 4: pip cache cleanup
        if 'pip install' in stripped.lower() and '--no-cache-dir' not in stripped:
             warnings.append({
                'line': line_num, 
                'severity': 'warning', 
                'message': 'Use `pip install --no-cache-dir` to prevent bloating the image with cache files.'
            })

        if stripped.upper().startswith('USER '):
            has_user = True

    # Rule 5: Running as root
    if not has_user:
         warnings.append({
            'line': 0, 
            'severity': 'error', 
            'message': 'Container is configured to run as root. Create and switch to a non-root user for security.'
        })
        
    return warnings

# --- CLI Commands ---

@app.command()
def analyze(image_name: str):
    """Analyze a Docker image and output a JSON report."""
    report = analyze_image_logic(image_name)
    print(json.dumps(report, indent=2))

@app.command()
def lint(dockerfile_path: str):
    """Lint a Dockerfile for anti-patterns."""
    try:
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        warnings = lint_dockerfile_logic(content)
        print(json.dumps(warnings, indent=2))
    except Exception as e:
        print(f"Error reading file {dockerfile_path}: {e}")
        raise typer.Exit(code=1)

# --- API Endpoints ---

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
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@api_app.post("/api/lint")
async def lint_dockerfile_endpoint(request: LintRequest):
    return lint_dockerfile_logic(request.dockerfile_content)

if __name__ == "__main__":
    app()
