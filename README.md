# DNS Resolution and Performance Analyzer

Computer Networking Lab, Project 18. Measures DNS response time with Python and `dig`,
compares three public resolvers, looks at record types and caching, and backs it up with a
packet capture.

## Setup (Ubuntu / WSL)

    sudo apt install -y dnsutils python3-venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Every query names its resolver with `@` (for example `@8.8.8.8`), because WSL's default
resolver did not answer in our setup.

## Run

    python parser.py             # parser self-test on 5 record types
    python main.py --test        # 1 domain, 1 resolver, 5 queries
    python main.py --full        # 10 domains x 3 resolvers x 5 A queries = 150 rows
    python analysis.py           # summary tables in data/
    python visualization.py      # 4 graphs in plots/
    python record_study.py       # A, AAAA, CNAME, MX, NS on 4 domains

`main.py --full` overwrites `data/raw_results.csv`, so copy it first if you want to keep a run.

## Files

- `config.py`: domains, resolvers, query count
- `dns_runner.py`: runs `dig` through `subprocess`
- `parser.py`: extracts status, query time, answer and TTL
- `main.py`: runs the experiment and writes the CSV
- `analysis.py`, `visualization.py`: statistics and graphs
- `record_study.py`: record type study
- `data/`: raw results, summaries, raw dig output, `dig +trace` output
- `plots/`: resolver comparison, cold vs warm, domain comparison, variability box plot
- `captures/`: DNS packet capture (`dns_github_A.pcap`)

## Main results (A records, 149 successful queries, one session)

| Resolver | Mean (ms) | Median (ms) | Min | Max |
|---|---|---|---|---|
| 1.1.1.1 | 21.45 | 19 | 11 | 75 |
| 8.8.8.8 | 28.20 | 23 | 15 | 67 |
| 9.9.9.9 | 36.52 | 27 | 23 | 351 |

- Overall range 11 to 351 ms, median 23 ms. One query (microsoft.com via 1.1.1.1) got no response.
- Repeated queries were not consistently faster. Only 9.9.9.9 showed a clear first-query
  penalty, driven by two spikes (351 ms and 115 ms).
- No consistent record-type effect: the ranking of record types changed from domain to domain.
- DNS is only one part of end-to-end latency (TCP, TLS, server time and transfer also add delay).

## Limitations

Single network and single session, small sample (10 first queries per resolver), timer
granularity of about 4 ms, popular domains likely already cached at the resolvers, and no
check of which cache layer answered. Differences between resolvers may reflect distance from
our location, not resolver quality.

## Environment
- OS: Ubuntu 26.04 LTS (WSL)
- Python: 
- dig: DiG 9.20.24-1ubuntu0.3-Ubuntu
