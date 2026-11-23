# Busca un fragmento normalizado y devuelve archivo y página.
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()
for arg in sys.argv[2:]:
    arch, frag = arg.split("|", 1)
    t = (Path(sys.argv[1]) / arch).read_text(encoding="utf-8")
    partes = re.split(r"=== PÁG (\d+) ===", t)
    hits = [partes[i] for i in range(1, len(partes), 2) if norm(frag) in norm(partes[i+1])]
    print(arch[:30], "|", frag[:60], "→ págs", hits)
