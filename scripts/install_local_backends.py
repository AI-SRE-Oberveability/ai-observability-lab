"""Download checksum-pinned Windows binaries into this workspace only."""

import hashlib
import json
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".runtime" / "backends"
LOCK = ROOT / "ai-observability-config/local/windows-binaries.lock.json"


def main():
    if sys.platform != "win32":
        raise SystemExit("Use Docker Compose on non-Windows hosts.")
    for name, item in json.loads(LOCK.read_text()).items():
        destination = RUNTIME / name
        destination.mkdir(parents=True, exist_ok=True)
        archive = destination / item["url"].rsplit("/", 1)[1]
        if not archive.exists():
            print(f"Downloading {name} {item['version']}", flush=True)
            urllib.request.urlretrieve(item["url"], archive)
        with archive.open("rb") as archive_stream:
            actual_hash = hashlib.file_digest(archive_stream, "sha256").hexdigest()
        if actual_hash != item["sha256"]:
            raise SystemExit(f"Checksum mismatch for {name}; no extraction performed.")
        # Extract just the executable from the verified archive, no archive paths used as targets.
        if archive.suffix == ".zip":
            with zipfile.ZipFile(archive) as package:
                members = [n for n in package.namelist() if n.endswith("/jaeger.exe")]
                if len(members) != 1:
                    raise SystemExit("Unexpected Jaeger archive layout")
                (destination / "jaeger.exe").write_bytes(package.read(members[0]))
        else:
            with tarfile.open(archive) as package:
                members = [
                    m for m in package if Path(m.name).name == "otelcol-contrib.exe"
                ]
                if len(members) != 1:
                    raise SystemExit("Unexpected Collector archive layout")
                (destination / "otelcol-contrib.exe").write_bytes(
                    package.extractfile(members[0]).read()
                )
        print(f"Verified {name} {item['version']}", flush=True)


if __name__ == "__main__":
    main()
