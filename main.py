import argparse
import csv
import os
from datetime import datetime, timezone

import config
from dns_runner import run_dig
from parser import parse_output

FIELDS = ["timestamp", "domain", "record_type", "dns_server", "query_number",
          "response_time_ms", "status", "answer", "ttl", "return_code"]

def run_experiment(domains, servers, record_types, queries, csv_path, raw_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    total = len(domains) * len(servers) * len(record_types) * queries
    done = 0
    with open(csv_path, "w", newline="") as f, open(raw_path, "w") as raw:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for domain in domains:
            for server in servers:
                for rtype in record_types:
                    for q in range(1, queries + 1):
                        out, err, code = run_dig(domain, rtype, server)
                        parsed = parse_output(out)
                        if parsed["status"] is None:
                            parsed["status"] = "NO_RESPONSE"   # keep failures, never delete
                        writer.writerow({
                            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "domain": domain,
                            "record_type": rtype,
                            "dns_server": server,
                            "query_number": q,
                            "response_time_ms": parsed["response_time_ms"],
                            "status": parsed["status"],
                            "answer": parsed["answer"],
                            "ttl": parsed["ttl"],
                            "return_code": code,
                        })
                        f.flush()
                        raw.write(f"=== {domain} {rtype} @{server} q{q} rc={code} ===\n{out}{err}\n")
                        done += 1
                        print(f"[{done}/{total}] {domain} {rtype} @{server} q{q}: "
                              f"{parsed['status']} {parsed['response_time_ms']} ms")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="1 domain, 1 resolver, 5 queries")
    ap.add_argument("--full", action="store_true", help="full experiment from config.py")
    args = ap.parse_args()

    if args.test:
        run_experiment(["github.com"], ["8.8.8.8"], ["A"], 5,
                       "data/test_results.csv", "data/test_raw_dig.txt")
    elif args.full:
        run_experiment(config.DOMAINS, config.DNS_SERVERS, config.RECORD_TYPES,
                       config.QUERIES_PER_COMBO,
                       "data/raw_results.csv", "data/raw_dig_output.txt")
    else:
        ap.print_help()
