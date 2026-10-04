import csv
import os
from datetime import datetime, timezone

import pandas as pd

from dns_runner import run_dig
from parser import parse_output

DOMAINS = ["google.com", "github.com", "www.github.com", "example.com"]
TYPES = ["A", "AAAA", "CNAME", "MX", "NS"]
SERVER = "8.8.8.8"
REPEATS = 3

FIELDS = ["timestamp", "domain", "record_type", "dns_server", "query_number",
          "response_time_ms", "status", "answer", "ttl", "return_code"]

os.makedirs("data", exist_ok=True)
rows = []
for domain in DOMAINS:
    for rtype in TYPES:
        for q in range(1, REPEATS + 1):
            out, err, code = run_dig(domain, rtype, SERVER)
            p = parse_output(out, rtype)
            status = p["status"] or "NO_RESPONSE"
            # NOERROR with an empty answer section = NODATA (record type not published)
            if status == "NOERROR" and p["answer"] is None:
                status = "NOERROR (NODATA)"
            rows.append({
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "domain": domain, "record_type": rtype, "dns_server": SERVER,
                "query_number": q, "response_time_ms": p["response_time_ms"],
                "status": status, "answer": p["answer"], "ttl": p["ttl"],
                "return_code": code,
            })
            print(f"{domain} {rtype} q{q}: {status} {p['response_time_ms']} ms")

with open("data/record_types.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)

df = pd.DataFrame(rows)

# Evidence table: one row per domain + record type
ev = (df.groupby(["domain", "record_type"])
        .agg(status=("status", "first"),
             answer=("answer", "first"),
             ttl=("ttl", "first"),
             median_ms=("response_time_ms", "median"))
        .reset_index())
ev["answer"] = ev["answer"].fillna("-").str.slice(0, 45)
print("\n== Record evidence table ==")
print(ev.to_string(index=False))

# Does record type affect response time?
bt = (df[df["status"].str.startswith("NOERROR")]
        .groupby("record_type")["response_time_ms"]
        .agg(["median", "mean", "min", "max", "count"]).round(2))
print("\n== Response time by record type ==")
print(bt)
ev.to_csv("data/record_evidence.csv", index=False)
