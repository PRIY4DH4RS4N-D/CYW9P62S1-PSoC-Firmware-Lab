"""Check preserved board files against the original source snapshot."""
import hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'docs/bsp-sha256.json').read_text())
for name, digest in manifest.items():
    path=root/'firmware/bsps'/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
        raise SystemExit(f'BSP mismatch: {name}')
print(f'PASS: {len(manifest)} preserved BSP/configuration files match source snapshot')
