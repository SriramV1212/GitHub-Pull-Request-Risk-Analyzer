import hmac       
import hashlib    
from fastapi import FastAPI, Request, HTTPException, Header
from app.config import GITHUB_WEBHOOK_SECRET
from app.db.session import init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    """Runs once when FastAPI starts — creates DB tables."""
    init_db()

@app.get("/health")
def health_check():
    """Simple check: is the server alive?"""
    return {"status": "ok"}

@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),  
):
    payload_bytes = await request.body()  # raw bytes of the incoming request


    if not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="Missing signature header")

    expected_sig = "sha256=" + hmac.new(
        key=GITHUB_WEBHOOK_SECRET.encode(),  
        msg=payload_bytes,                   
        digestmod=hashlib.sha256             
    ).hexdigest()                            

    # compare_digest prevents timing attacks (safer than ==)
    if not hmac.compare_digest(expected_sig, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    action = payload.get("action")
    if action not in ("opened", "synchronize"):
        # We only care about new PRs and updated PRs
        return {"message": f"Ignoring action: {action}"}

    pr         = payload["pull_request"]
    pr_number  = pr["number"]
    pr_title   = pr["title"]
    pr_url     = pr["html_url"]
    head_sha   = pr["head"]["sha"]
    base_sha   = pr["base"]["sha"]
    repo_full_name = payload["repository"]["full_name"]

    from app.tasks import analyze_pr   # imported here to avoid circular imports
    analyze_pr.delay(
        pr_number=pr_number,
        repo_full_name=repo_full_name,
        head_sha=head_sha,
        base_sha=base_sha,
        pr_title=pr_title,
        pr_url=pr_url,
    )

    return {"message": "PR queued for analysis", "pr_number": pr_number}