import os
from pathlib import Path
from urllib.request import Request, urlopen

url=os.environ.get("KEY_API_URL","http://127.0.0.1:5000").rstrip("/")+"/stats"
secret=os.environ.get("KEY_API_SECRET","").strip()
if not secret:
    p=Path(os.path.expanduser("~/key-api/.api_secret"))
    secret=p.read_text().strip() if p.exists() else ""
req=Request(url,headers={"Authorization":"Bearer "+secret})
with urlopen(req,timeout=5) as r:
    print(r.status, r.read().decode())
