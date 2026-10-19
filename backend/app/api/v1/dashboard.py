from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path
import io

from app.dashboard_template import build_dashboard_html

router = APIRouter()

# In-memory store for the active dashboard
_LATEST_DASHBOARD_HTML: str = """<!DOCTYPE html>
<html>
<head><title>Autonomous Data Analyst Dashboard</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-slate-900 text-white min-h-screen flex items-center justify-center p-6">
    <div class="max-w-md w-full bg-slate-800 p-8 rounded-xl border border-slate-700 text-center shadow-xl">
        <h1 class="text-xl font-bold text-slate-100">No Dataset Uploaded Yet</h1>
        <p class="text-sm text-slate-400 mt-2">Upload a CSV, Excel, or JSON file via the API or dashboard endpoint to see live interactive visualizations.</p>
    </div>
</body>
</html>"""

@router.post("/generate-dashboard", summary="Generate interactive dashboard from uploaded data")
async def generate_dashboard(
    file: UploadFile = File(...),
) -> dict:
    """Accept CSV/Excel/JSON, generate interactive dashboard, return access links."""
    global _LATEST_DASHBOARD_HTML
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
        
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".csv", ".json", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file format {suffix}. Please upload CSV, JSON, or Excel.")
    
    contents = await file.read()
    try:
        if suffix == ".csv":
            df = pd.read_csv(io.BytesIO(contents))
        elif suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(io.BytesIO(contents))
        elif suffix == ".json":
            df = pd.read_json(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    # Generate interactive HTML dashboard
    title = f"{file.filename} - Interactive Dashboard"
    html_content = build_dashboard_html(df, title=title)
    _LATEST_DASHBOARD_HTML = html_content

    # Save to disk as well
    try:
        dash_file = Path("/tmp/latest_dashboard.html")
        dash_file.write_text(html_content, encoding="utf-8")
    except Exception:
        pass

    dashboard_url = "http://localhost:8000/dashboard"
    sidecar_link = "sidecar://localhost:8000/dashboard"

    return {
        "message": "Dashboard ready",
        "url": dashboard_url,
        "sidecar": sidecar_link,
        "rows": len(df),
        "columns": list(df.columns)
    }

@router.get("/generate-dashboard", summary="View latest interactive dashboard", response_class=HTMLResponse)
async def view_dashboard_v1():
    """Render the latest generated dashboard directly in the browser."""
    return HTMLResponse(content=_LATEST_DASHBOARD_HTML)

@router.get("/dashboard", summary="View latest interactive dashboard", response_class=HTMLResponse)
async def view_dashboard_root():
    """Direct shortcut to view the latest interactive dashboard."""
    return HTMLResponse(content=_LATEST_DASHBOARD_HTML)