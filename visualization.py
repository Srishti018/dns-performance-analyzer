import matplotlib
matplotlib.use("Agg")          # save to files, no display needed in WSL
import matplotlib.pyplot as plt
import os
from analysis import load, ok_a_queries

os.makedirs("plots", exist_ok=True)
df = load()
a = ok_a_queries(df)
servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]

# Graph 1: mean (with median) response time by resolver
g = a.groupby("dns_server")["response_time_ms"].agg(["mean", "median"]).reindex(servers)
ax = g.plot(kind="bar", figsize=(7, 4.5), rot=0)
ax.set_title("A record response time by DNS resolver")
ax.set_xlabel("Resolver"); ax.set_ylabel("Response time (ms)")
plt.tight_layout(); plt.savefig("plots/resolver_comparison.png", dpi=150); plt.close()

# Graph 2: first query vs later queries
a["phase"] = a["query_number"].apply(lambda q: "Q1 (cold)" if q == 1 else "Q2-Q5 (warm)")
cw = a.groupby(["dns_server", "phase"])["response_time_ms"].mean().unstack().reindex(servers)
ax = cw.plot(kind="bar", figsize=(7, 4.5), rot=0)
ax.set_title("First query vs later queries (mean)")
ax.set_xlabel("Resolver"); ax.set_ylabel("Response time (ms)")
plt.tight_layout(); plt.savefig("plots/cold_vs_warm.png", dpi=150); plt.close()

# Graph 3: mean response time by domain
d = a.groupby("domain")["response_time_ms"].mean().sort_values()
ax = d.plot(kind="barh", figsize=(7, 5))
ax.set_title("Mean A record response time by domain (all resolvers)")
ax.set_xlabel("Response time (ms)")
plt.tight_layout(); plt.savefig("plots/domain_comparison.png", dpi=150); plt.close()

# Graph 4: variability (box plot)
data = [a[a.dns_server == s]["response_time_ms"] for s in servers]
plt.figure(figsize=(7, 4.5))
plt.boxplot(data, tick_labels=servers)
plt.title("Response time variability by resolver")
plt.xlabel("Resolver"); plt.ylabel("Response time (ms)")
plt.tight_layout(); plt.savefig("plots/variability_boxplot.png", dpi=150); plt.close()

print("Saved 4 plots in plots/")
