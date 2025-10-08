from fastapi import FastAPI, Response, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .scraper import scrape_url
from .enricher import extract_emails, extract_phones
from .extractor import extract_with_llm
from .deduplicator import deduplicate_leads
from .scorer import score_lead, get_score_justification
import json
import csv
import io
from urllib.parse import urlparse
import base64

app = FastAPI()
router = APIRouter()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class URL(BaseModel):
    url: str


class Leads(BaseModel):
    leads: list[dict]


@router.post("/scrape/")
def process_url(url: URL):
    """
    Scrapes a URL, extracts emails and phone numbers, and returns the data.
    """
    html_content = scrape_url(url.url)
    if not html_content:
        return {"error": "Failed to fetch URL"}

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()

    emails = extract_emails(text)
    phones = extract_phones(text)

    return {
        "url": url.url,
        "emails": emails,
        "phones": phones,
    }


@router.post("/extract/")
def process_url_with_llm(url: URL):
    """
    Scrapes a URL and uses an LLM to extract structured data.
    """
    html_content = scrape_url(url.url)
    if not html_content:
        return {"error": "Failed to fetch URL"}

    extracted_llm = extract_with_llm(html_content) or {}

    # Heuristic extraction (regex + simple page signals)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(" ", strip=True)

    heuristic_emails = extract_emails(text)
    heuristic_phones = extract_phones(text)

    # Detect presence of common pages/phrases
    has_contact_page = any(
        (a.get("href") or "").lower().find("contact") != -1 for a in soup.find_all("a")
    )
    pricing_keywords = ["pricing", "plans", "subscribe", "buy now"]
    has_pricing = any(kw in text.lower() for kw in pricing_keywords)

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    # Domain from the URL
    try:
        parsed = urlparse(url.url)
        domain = parsed.netloc or None
        if domain and domain.startswith("www."):
            domain = domain[4:]
    except Exception:
        domain = None

    # Merge LLM and heuristic outputs conservatively
    merged = {
        "company_name": extracted_llm.get("company_name"),
        "domain": extracted_llm.get("domain") or domain,
        "emails": sorted(
            list({*(extracted_llm.get("emails", []) or []), *heuristic_emails})
        ),
        "phones": sorted(
            list({*(extracted_llm.get("phones", []) or []), *heuristic_phones})
        ),
        "linkedin": extracted_llm.get("linkedin"),
        "has_contact_page": bool(
            extracted_llm.get("has_contact_page") or has_contact_page
        ),
        "has_pricing": bool(extracted_llm.get("has_pricing") or has_pricing),
        "intent_phrases": extracted_llm.get("intent_phrases") or [],
        "title": extracted_llm.get("title") or title,
        "raw_snippet": extracted_llm.get("raw_snippet"),
        "industry": extracted_llm.get("industry"),
        "tech_stack": extracted_llm.get("tech_stack") or [],
    }

    return {
        "url": url.url,
        "data": merged,
    }


@router.post("/process_leads/")
def process_leads(leads: Leads):
    """
    Deduplicates and scores a list of leads.
    """
    deduplicated_leads = deduplicate_leads(leads.leads)
    scored_leads = []
    for lead in deduplicated_leads:
        score, breakdown = score_lead(lead)
        justification = get_score_justification(lead, score, breakdown)
        lead["score"] = score
        lead["score_breakdown"] = breakdown
        lead["justification"] = justification
        scored_leads.append(lead)

    return {"processed_leads": scored_leads}


@router.post("/export_leads/")
def export_leads(leads: Leads):
    """
    Exports a list of leads to a CSV file.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = [
        "id",
        "company_name",
        "domain",
        "emails",
        "phones",
        "linkedin",
        "has_contact_page",
        "has_pricing",
        "estimated_revenue",
        "score",
        "score_breakdown",
        "justification",
        "source_urls",
    ]
    writer.writerow(header)

    # Write rows
    for i, lead in enumerate(leads.leads):
        row = [
            i,
            lead.get("company_name"),
            lead.get("domain"),
            ",".join(lead.get("emails", [])),
            ",".join(lead.get("phones", [])),
            lead.get("linkedin"),
            lead.get("has_contact_page"),
            lead.get("has_pricing"),
            lead.get("estimated_revenue"),
            lead.get("score"),
            json.dumps(lead.get("score_breakdown", {})),
            lead.get("justification"),
            ",".join(lead.get("source_urls", [])),
        ]
        writer.writerow(row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


app.include_router(router, prefix="/api")

# Mount frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/favicon.ico")
def favicon():
    """
    Serve a tiny 1x1 PNG favicon to avoid 404s in local/dev.
    """
    # Transparent 1x1 PNG
    png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Uu1q9kAAAAASUVORK5CYII="
    png_bytes = base64.b64decode(png_base64)
    return Response(content=png_bytes, media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
