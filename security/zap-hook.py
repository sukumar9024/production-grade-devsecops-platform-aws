"""ZAP hook: authenticate for a time-bounded scan; never log bearer tokens."""
import json
import os
import re
import time
import urllib.request

token = None
refreshed = 0


def zap_started(zap, target):
    global token, refreshed
    base = os.environ["DAST_URL"].rstrip("/")
    request = urllib.request.Request(base + "/api/v1/auth/login", data=json.dumps({
        "identity": os.environ["SMOKE_IDENTITY"], "password": os.environ["SMOKE_PASSWORD"]
    }).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        token = json.load(response)["access_token"]
    zap.replacer.add_rule("SecureOps staging auth", True, "REQ_HEADER", False,
                          "Authorization", "Bearer " + token, url="^" + re.escape(base) + "/")
    refreshed = time.time()


def zap_access_target(zap, target):
    if not token:
        raise RuntimeError("Authenticated scan requires a valid access token")
