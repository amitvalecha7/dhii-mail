import json
import urllib.request
import urllib.error
from pathlib import Path

req_path = Path("requirements.txt")

try:
    text = req_path.read_text(encoding="utf-8")
except FileNotFoundError:
    print("ERROR: requirements.txt not found")
    raise SystemExit(1)

lines = text.splitlines()

try:
    from packaging.version import Version, InvalidVersion  # type: ignore
except Exception:  # packaging not available
    Version = None
    InvalidVersion = Exception

problems = []

for idx, raw in enumerate(lines, 1):
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if "==" not in line:
        continue

    left, version = line.split("==", 1)
    name_full = left.strip()
    version = version.strip().split()[0]

    base_name = name_full.split("[", 1)[0].strip()

    url = f"https://pypi.org/pypi/{base_name}/json"

    try:
        with urllib.request.urlopen(url) as resp:
            if resp.status != 200:
                problems.append({
                    "line": idx,
                    "requirement": line,
                    "package": base_name,
                    "version": version,
                    "status": "package_lookup_http_error",
                    "http_status": resp.status,
                })
                continue
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            problems.append({
                "line": idx,
                "requirement": line,
                "package": base_name,
                "version": version,
                "status": "missing_package",
                "http_status": e.code,
            })
        else:
            problems.append({
                "line": idx,
                "requirement": line,
                "package": base_name,
                "version": version,
                "status": "package_lookup_http_error",
                "http_status": e.code,
            })
        continue
    except Exception as e:
        problems.append({
            "line": idx,
            "requirement": line,
            "package": base_name,
            "version": version,
            "status": "package_lookup_exception",
            "error": str(e),
        })
        continue

    releases = data.get("releases", {}) or {}

    if version in releases and releases[version]:
        continue

    available_versions = [v for v, files in releases.items() if files]
    suggested = None

    if available_versions:
        if Version is not None:
            try:
                target = Version(version)
                parsed = []
                for v in available_versions:
                    try:
                        parsed.append(Version(v))
                    except InvalidVersion:
                        continue
                parsed.sort()
                lower_or_equal = [v for v in parsed if v <= target]
                if lower_or_equal:
                    suggested = str(lower_or_equal[-1])
                else:
                    suggested = str(parsed[0])
            except Exception:
                suggested = sorted(available_versions)[-1]
        else:
            suggested = sorted(available_versions)[-1]

    problems.append({
        "line": idx,
        "requirement": line,
        "package": base_name,
        "version": version,
        "status": "missing_version" if available_versions else "no_releases",
        "suggested_version": suggested,
        "available_versions_sample": sorted(available_versions)[-5:],
    })

# Print a concise, human-readable summary
if not problems:
    print("All pinned versions match real PyPI releases.")
else:
    print("Found problematic pinned requirements (line: requirement -> status / suggestion):")
    for p in problems:
        status = p["status"]
        sugg = p.get("suggested_version")
        extra = ""
        if status == "missing_version" and sugg:
            extra = f" (suggested: {p['package']}=={sugg})"
        elif status == "missing_package":
            extra = " (no such package on PyPI)"
        print(f"  L{p['line']}: {p['requirement']} -> {status}{extra}")

# Also dump full JSON for reference
print("\nJSON:")
print(json.dumps({"problems": problems}, indent=2))
