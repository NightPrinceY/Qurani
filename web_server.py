"""
Simple web server to serve the interface
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

app = FastAPI(title="Quran Memorization Assistant - Web Interface")

# Mount static files
web_dir = Path(__file__).parent / "web_interface"
assets_dir = Path(__file__).parent / "assets"

# Mount assets directory as static files
app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Serve CSS and JS files
@app.get("/style.css")
async def get_css():
    css_file = web_dir / "style.css"
    if css_file.exists():
        return FileResponse(str(css_file), media_type="text/css")
    return {"error": "CSS not found"}

@app.get("/app.js")
async def get_js():
    js_file = web_dir / "app.js"
    if js_file.exists():
        return FileResponse(str(js_file), media_type="application/javascript")
    return {"error": "JS not found"}

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return {"error": "Interface not found"}

@app.get("/test")
async def test_services():
    """Serve the service testing interface"""
    test_file = web_dir / "test_services.html"
    if test_file.exists():
        return FileResponse(str(test_file), media_type="text/html")
    return {"error": "Test interface not found"}

@app.get("/background.gif")
async def get_background():
    """Serve background GIF"""
    bg_file = assets_dir / "background.gif"
    if bg_file.exists():
        return FileResponse(
            str(bg_file),
            media_type="image/gif",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    return {"error": "Background GIF not found", "path": str(bg_file)}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "web_interface"}

if __name__ == "__main__":
    print("=" * 60)
    print("🌐 Starting Web Interface Server")
    print("=" * 60)
    print("\n📖 Open your browser and go to:")
    print("   http://localhost:8080")
    print("\n⚠️  Make sure all backend services are running!")
    print("   Run: python start_services.py")
    print("\n" + "=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

