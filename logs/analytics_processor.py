#!/usr/bin/env python3
import os, json, time, re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from clickhouse_driver import Client
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

try:
    import google.generativeai as genai
except Exception:
    genai = None

# --- Config ---
CH_HOST = os.getenv("CH_HOST", "localhost")
CH_PORT = int(os.getenv("CH_PORT", "9000"))
CH_DB = os.getenv("CH_DB", "logs_db")
CH_USER = os.getenv("CH_USER", "default")
CH_PASS = os.getenv("CH_PASS", "your_secure_password")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DEFAULT_SINCE_HOURS = int(os.getenv("SINCE_HOURS", "168"))
TIME_BUCKET_MIN = int(os.getenv("TIME_BUCKET_MIN", "60"))
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "dashboard_report.json")
LLM_SAMPLE_LIMIT = int(os.getenv("LLM_SAMPLE_LIMIT", "600"))

TOOL_TABLE_PREFIX = "tool_"
SECURITY_TABLE = "security_logs_logs"

# Create FastAPI app
app = FastAPI(
    title="Analytics API",
    description="API for analytics from ClickHouse logs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ClickHouse wrapper ---
class CH:
    def __init__(self):
        self.client = Client(
            host=CH_HOST,
            port=CH_PORT,
            user=CH_USER,
            password=CH_PASS,
            database=CH_DB
        )
    def tables(self):
        return [t[0] for t in self.client.execute("SHOW TABLES")]
    def query(self, q, params=None):
        return self.client.execute(q, params or {})

# --- Helper SQL snippets ---
def since_clause(hours=None):
    hours = hours if hours is not None else DEFAULT_SINCE_HOURS
    dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    return f"timestamp >= toDateTime('{dt.strftime('%Y-%m-%d %H:%M:%S')}')"

def base_cols():
    return "timestamp, tool_name, arguments, result, success, error, response_time_ms"

def select_union_all(ch, tables, where):
    selects = []
    for t in tables:
        selects.append(f"SELECT {base_cols()} FROM {CH_DB}.{t} WHERE {where}")
    return " \nUNION ALL\n".join(selects)

# --- Analytics queries ---
def overview(ch, tables, hours=None):
    where = since_clause(hours)
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT
      count() AS total_requests,
      sumIf(1, success=1) AS total_success,
      sumIf(1, success=0) AS total_errors,
      avg(response_time_ms) AS avg_latency_ms,
      quantile(0.95)(response_time_ms) AS p95_latency_ms
    FROM all_logs
    """
    r = ch.query(q)[0]
    return {
        "total_requests": int(r[0]),
        "total_success": int(r[1]),
        "total_errors": int(r[2]),
        "avg_latency_ms": float(r[3] or 0),
        "p95_latency_ms": float(r[4] or 0),
    }

def usage_timeseries(ch, tables, hours=None, bucket_min=None):
    where = since_clause(hours)
    bucket = bucket_min if bucket_min is not None else TIME_BUCKET_MIN
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT
      toStartOfInterval(timestamp, INTERVAL {bucket} minute) AS bucket,
      count() AS n,
      sumIf(1, success=1) AS s,
      sumIf(1, success=0) AS e
    FROM all_logs
    GROUP BY bucket
    ORDER BY bucket
    """
    rows = ch.query(q)
    return [{
        "bucket": rows[i][0].isoformat(),
        "requests": int(rows[i][1]),
        "success": int(rows[i][2]),
        "errors": int(rows[i][3]),
    } for i in range(len(rows))]

def usage_by_tool(ch, tables, hours=None):
    where = since_clause(hours)
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT tool_name, count() AS n, sumIf(1, success=1) AS s, sumIf(1, success=0) AS e,
           avg(response_time_ms) AS avg_ms, quantile(0.95)(response_time_ms) AS p95_ms
    FROM all_logs
    GROUP BY tool_name
    ORDER BY n DESC
    """
    rows = ch.query(q)
    return [{
        "tool_name": r[0],
        "requests": int(r[1]),
        "success": int(r[2]),
        "errors": int(r[3]),
        "avg_latency_ms": float(r[4] or 0),
        "p95_latency_ms": float(r[5] or 0),
    } for r in rows]

def heatmap(ch, tables, hours=None):
    where = since_clause(hours)
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT
      toDayOfWeek(timestamp) AS dow, toHour(timestamp) AS hour, count() AS n
    FROM all_logs
    GROUP BY dow, hour
    ORDER BY dow, hour
    """
    rows = ch.query(q)
    return [{"dow": int(r[0]), "hour": int(r[1]), "requests": int(r[2])} for r in rows]

def error_breakdown(ch, tables, hours=None, limit=20):
    where = since_clause(hours)
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT
      tool_name, error, count() AS n
    FROM all_logs
    WHERE success=0 AND error!=''
    GROUP BY tool_name, error
    ORDER BY n DESC
    LIMIT {limit}
    """
    rows = ch.query(q)
    return [{"tool_name": r[0], "error": r[1], "count": int(r[2])} for r in rows]

def latency_distribution(ch, tables, hours=None, bins=(0,50,100,200,500,1000,2000,5000,10000,60000)):
    where = since_clause(hours)
    conds = []
    for i in range(len(bins)-1):
        conds.append(f"sumIf(1, response_time_ms>={bins[i]} AND response_time_ms<{bins[i+1]}) AS b{i}")
    conds.append(f"sumIf(1, response_time_ms>={bins[-1]}) AS b{len(bins)-1}")
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT {", ".join(conds)} FROM all_logs
    """
    r = ch.query(q)[0] if ch.query(q) else []
    out = []
    for i in range(len(bins)-1):
        out.append({"range_ms": [bins[i], bins[i+1]], "count": int(r[i] or 0)})
    out.append({"range_ms": [bins[-1], None], "count": int(r[len(bins)-1] or 0)})
    return out

def search_analytics(ch, tables, hours=None):
    search_tables = [t for t in tables if t.startswith(f"{TOOL_TABLE_PREFIX}search_")]
    if not search_tables: return {"by_category": [], "top_errors": [], "latency": []}
    where = since_clause(hours)
    q1 = f"""
    WITH all_logs AS ({select_union_all(ch, search_tables, where)})
    SELECT tool_name, count() AS n, sumIf(1, success=1) AS s, sumIf(1, success=0) AS e
    FROM all_logs
    GROUP BY tool_name ORDER BY n DESC
    """
    q2 = f"""
    WITH all_logs AS ({select_union_all(ch, search_tables, where)})
    SELECT error, count() AS n FROM all_logs WHERE success=0 AND error!='' GROUP BY error ORDER BY n DESC LIMIT 10
    """
    q3 = f"""
    WITH all_logs AS ({select_union_all(ch, search_tables, where)})
    SELECT tool_name, avg(response_time_ms) AS avg_ms, quantile(0.95)(response_time_ms) AS p95_ms
    FROM all_logs GROUP BY tool_name ORDER BY avg_ms DESC
    """
    cat = [{"tool_name": r[0], "requests": int(r[1]), "success": int(r[2]), "errors": int(r[3])} for r in ch.query(q1)]
    terr = [{"error": r[0], "count": int(r[1])} for r in ch.query(q2)]
    lat = [{"tool_name": r[0], "avg_latency_ms": float(r[1] or 0), "p95_latency_ms": float(r[2] or 0)} for r in ch.query(q3)]
    return {"by_category": cat, "top_errors": terr, "latency": lat}

def claims_contracts_kpis(ch, tables, hours=None):
    cc_tables = [t for t in tables if t.startswith(f"{TOOL_TABLE_PREFIX}get_")]
    if not cc_tables: 
        return {}
    where = since_clause(hours)
    
    total_success = 0
    total_errors = 0
    all_response_times = []
    
    for table in cc_tables:
        q_success = f"SELECT count() FROM {CH_DB}.{table} WHERE {where} AND success=1"
        success_result = ch.query(q_success)
        if success_result:
            total_success += int(success_result[0][0])
        
        q_errors = f"SELECT count() FROM {CH_DB}.{table} WHERE {where} AND success=0"
        error_result = ch.query(q_errors)
        if error_result:
            total_errors += int(error_result[0][0])
        
        q_times = f"SELECT response_time_ms FROM {CH_DB}.{table} WHERE {where}"
        times_result = ch.query(q_times)
        if times_result:
            all_response_times.extend([float(row[0]) for row in times_result if row[0] is not None])
    
    if all_response_times:
        avg_ms = sum(all_response_times) / len(all_response_times)
        sorted_times = sorted(all_response_times)
        p95_index = int(0.95 * len(sorted_times))
        p95_ms = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
    else:
        avg_ms = 0
        p95_ms = 0
    
    return {
        "success": total_success,
        "errors": total_errors,
        "avg_latency_ms": avg_ms,
        "p95_latency_ms": p95_ms,
    }

# --- Data anonymization for LLM ---
def anonymize_text(text):
    if not text or not isinstance(text, str):
        return text
    text = re.sub(r'\b\d{6,}\b', '[REDACTED_NUMBER]', text)
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', text)
    text = re.sub(r'\+?\d[\d\s\-]{7,}', '[REDACTED_PHONE]', text)
    return text

def sample_for_llm(ch, tables, hours=None, limit=None):
    where = since_clause(hours)
    sample_limit = limit if limit is not None else LLM_SAMPLE_LIMIT
    q = f"""
    WITH all_logs AS ({select_union_all(ch, tables, where)})
    SELECT timestamp, tool_name, arguments, result, success, error, response_time_ms
    FROM all_logs
    ORDER BY timestamp DESC
    LIMIT {sample_limit}
    """
    rows = ch.query(q)
    out = []
    for r in rows:
        out.append({
            "timestamp": r[0].isoformat(),
            "tool_name": r[1],
            "arguments": anonymize_text(r[2]),
            "result": anonymize_text(r[3]),
            "success": int(r[4]),
            "error": anonymize_text(r[5]),
            "response_time_ms": float(r[6] or 0),
        })
    return out

def llm_insights(samples):
    if not GOOGLE_API_KEY or not genai:
        return {"note": "LLM disabled; set GOOGLE_API_KEY to enable."}
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "You analyze chatbot tool logs for an insurance admin dashboard. "
        "The data has been anonymized; do not attempt to reconstruct identities. "
        "Produce concise insights in JSON with keys: "
        "{'trending_topics':[], 'recurring_failures':[], 'knowledge_gaps':[], 'action_items':[], 'observations':[]}. "
        "Group semantically similar queries. Be concrete and brief."
    )
    try:
        content = json.dumps(samples)[:900000]
        resp = model.generate_content([prompt, content])
        text = resp.text.strip()
        try:
            return json.loads(text)
        except Exception:
            return {"raw": text}
    except Exception as e:
        return {"error": str(e)}

# --- Report builder ---
def build_report(hours=None, bucket_min=None, llm_limit=None):
    ch = CH()
    all_tables = ch.tables()
    tool_tables = [t for t in all_tables if t.startswith(TOOL_TABLE_PREFIX)]
    
    report = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "database": CH_DB,
            "since_hours": hours if hours is not None else DEFAULT_SINCE_HOURS,
            "time_bucket_min": bucket_min if bucket_min is not None else TIME_BUCKET_MIN,
            "tables_considered": tool_tables,
        },
        "overview": overview(ch, tool_tables, hours),
        "timeseries": usage_timeseries(ch, tool_tables, hours, bucket_min),
        "usage_by_tool": usage_by_tool(ch, tool_tables, hours),
        "heatmap": heatmap(ch, tool_tables, hours),
        "latency_distribution": latency_distribution(ch, tool_tables, hours),
        "error_breakdown": error_breakdown(ch, tool_tables, hours),
        "search": search_analytics(ch, tool_tables, hours),
        "claims_contracts_kpis": claims_contracts_kpis(ch, tool_tables, hours),
        "llm_insights": llm_insights(sample_for_llm(ch, tool_tables, hours, llm_limit)),
    }

    return report

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Analytics API is running", "endpoints": ["/analytics", "/healthcheck"]}

@app.get("/healthcheck")
def healthcheck():
    try:
        ch = CH()
        tables = ch.tables()
        return {"status": "ok", "tables_count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/analytics")
def get_analytics(
    hours: Optional[int] = Query(None, description="Hours to look back"),
    bucket_min: Optional[int] = Query(None, description="Time bucket size in minutes"),
    llm_limit: Optional[int] = Query(None, description="Limit for LLM samples")
):
    try:
        report = build_report(hours, bucket_min, llm_limit)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

# Start server if running as script
if __name__ == "__main__":
    uvicorn.run("analytics_processor:app", host="0.0.0.0", port=6002, reload=True)