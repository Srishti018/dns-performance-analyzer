import pandas as pd

def load(path="data/raw_results.csv"):
    df = pd.read_csv(path)
    df["response_time_ms"] = pd.to_numeric(df["response_time_ms"], errors="coerce")
    return df

def ok_a_queries(df):
    """Successful A-record queries only (failures are reported separately)."""
    return df[(df["record_type"] == "A") & (df["status"] == "NOERROR")].copy()

def resolver_summary(df):
    a = ok_a_queries(df)
    return (a.groupby("dns_server")["response_time_ms"]
              .agg(["mean", "median", "min", "max", "std", "count"])
              .round(2).reset_index())

def cold_warm(df):
    a = ok_a_queries(df)
    a["phase"] = a["query_number"].apply(lambda q: "cold (Q1)" if q == 1 else "warm (Q2-Q5)")
    return (a.groupby(["dns_server", "phase"])["response_time_ms"]
              .agg(["mean", "median", "count"]).round(2).reset_index())

def domain_summary(df):
    a = ok_a_queries(df)
    return (a.groupby("domain")["response_time_ms"]
              .agg(["mean", "median", "min", "max"]).round(2).reset_index())

def failures(df):
    return df[df["status"] != "NOERROR"]

if __name__ == "__main__":
    df = load()
    rs, cw, ds, fl = resolver_summary(df), cold_warm(df), domain_summary(df), failures(df)
    rs.to_csv("data/summary.csv", index=False)
    cw.to_csv("data/cold_warm.csv", index=False)
    ds.to_csv("data/domain_summary.csv", index=False)
    fl.to_csv("data/failures.csv", index=False)
    print("\n== By resolver (A records, successful queries) ==\n", rs)
    print("\n== Cold vs warm ==\n", cw)
    print("\n== By domain ==\n", ds)
    print("\n== Failed / non-NOERROR observations ==\n",
          fl[["domain", "dns_server", "query_number", "status"]])
    a = ok_a_queries(df)
    print("\nOverall: min", a.response_time_ms.min(), "max", a.response_time_ms.max(),
          "mean", round(a.response_time_ms.mean(), 2),
          "median", a.response_time_ms.median())
