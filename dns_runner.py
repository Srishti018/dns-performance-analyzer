import subprocess

def run_dig(domain, record_type, dns_server):
    command = [
        "dig", f"@{dns_server}", domain, record_type,
        "+time=3", "+tries=1"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

if __name__ == "__main__":
    out, err, code = run_dig("github.com", "A", "8.8.8.8")
    print(out)
    print("Return code:", code)
