import asyncio, json, re, time, httpx
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

BASE = Path(__file__).parent
app = FastAPI()
SITES = json.load(open(BASE / "sites.json"))

hits = {}

def too_many(request, cost):
    fwd = request.headers.get("x-forwarded-for")
    ip = fwd.split(",")[-1].strip() if fwd else request.client.host
    now = time.time()
    recent = [t for t in hits.get(ip, []) if now - t < 60]
    if len(recent) + cost > 12:
        hits[ip] = recent
        return True
    hits[ip] = recent + [now] * cost
    return False

@app.get("/")
def home():
    return FileResponse(BASE.parent / "frontend" / "index.html")

async def check(client, site, username):
    url = site["url"].format(username)
    try:
        r = await client.get(url, timeout=8)
        status = "possible match" if r.status_code == 200 else "not found"
    except Exception:
        status = "couldn't check"
    return {"site": site["name"], "url": url, "status": status}

@app.get("/search")
async def search(request: Request, username: str):
    if too_many(request, 1):
        return JSONResponse({"error": "Too many searches. Please wait a minute."}, status_code=429)
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,30}", username):
        return {"error": "Invalid username"}
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        results = await asyncio.gather(*[check(client, s, username) for s in SITES])
    return {"username": username, "results": results}

def variants(name):
    parts = re.sub(r"[^a-z\s]", "", name.lower()).split()
    if len(parts) < 2:
        return []
    f, l = parts[0], parts[-1]
    return list({f + l, f + "." + l, f + "_" + l, f[0] + l, f + l[0]})

@app.get("/name-search")
async def name_search(request: Request, name: str):
    if too_many(request, 4):
        return JSONResponse({"error": "Too many searches. Please wait a minute."}, status_code=429)
    names = variants(name) if len(name) <= 60 else []
    if not names:
        return {"error": "Please enter a first and last name"}
    headers = {"User-Agent": "Mozilla/5.0"}
    pairs = [(u, s) for u in names for s in SITES]
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        results = await asyncio.gather(*[check(client, s, u) for u, s in pairs])
    for (u, s), r in zip(pairs, results):
        r["username"] = u
    matches = [r for r in results if r["status"] == "possible match"]
    return {"name": name, "tried": names, "results": matches}