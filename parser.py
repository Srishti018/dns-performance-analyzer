def parse_query_time(output):
    for line in output.splitlines():
        if "Query time:" in line:
            value = line.split("Query time:")[1].strip()
            return float(value.split()[0])
    return None

def parse_status(output):
    for line in output.splitlines():
        if "status:" in line:
            return line.split("status:")[1].split(",")[0].strip()
    return None

def parse_answers(output, rtype=None):
    """Return (answer_string, ttl) from the ANSWER SECTION."""
    answers = []
    ttl = None
    in_answer = False
    for line in output.splitlines():
        if line.startswith(";; ANSWER SECTION:"):
            in_answer = True
            continue
        if in_answer:
            if not line.strip():
                break
            parts = line.split()
            # format: name ttl IN type data...
            if len(parts) >= 5 and (rtype is None or parts[3] == rtype):
                if ttl is None:
                    ttl = int(parts[1])
                answers.append(" ".join(parts[4:]))
    return "; ".join(answers) if answers else None, ttl

def parse_output(output, rtype=None):
    answer, ttl = parse_answers(output, rtype)
    return {
        "status": parse_status(output),
        "response_time_ms": parse_query_time(output),
        "answer": answer,
        "ttl": ttl,
    }

if __name__ == "__main__":
    from dns_runner import run_dig
    tests = [
        ("github.com", "A", "8.8.8.8"),
        ("google.com", "AAAA", "1.1.1.1"),
        ("google.com", "MX", "9.9.9.9"),
        ("google.com", "NS", "8.8.8.8"),
        ("www.github.com", "CNAME", "8.8.8.8"),
    ]
    for domain, rtype, server in tests:
        out, err, code = run_dig(domain, rtype, server)
        print(domain, rtype, server, "->", parse_output(out), "| rc:", code)
