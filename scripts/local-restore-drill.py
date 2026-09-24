#!/usr/bin/env python3
"""Dump the LOCAL Compose DB, restore into a new database, and compare data hashes."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    os.umask(0o077)
    container = subprocess.check_output(["docker", "compose", "ps", "-q", "postgres"], text=True).strip()
    if not container:
        raise SystemExit("Start the local Compose PostgreSQL service first")
    temporary = "secureops_restore_" + uuid.uuid4().hex[:12]
    directory = root / ".runtime/backups"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    dump = directory / (temporary + ".dump")
    record = {"scope": "local PostgreSQL only; not an RDS restore", "backup_time": now(),
              "target": temporary, "validation": "pending"}

    def sql(database, statement):
        return subprocess.check_output(["docker", "exec", container, "psql", "-X", "-U", "secureops",
            "-d", database, "-A", "-t", "-v", "ON_ERROR_STOP=1", "-c", statement], text=True).strip()

    def fingerprint(database):
        result = {}
        for table in sql(database, "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").splitlines():
            if not table.replace("_", "").isalnum():
                raise ValueError("Unexpected table identifier")
            data = sql(database, f'SELECT row_to_json(t)::text FROM "{table}" t ORDER BY row_to_json(t)::text')
            result[table] = hashlib.sha256(data.encode()).hexdigest()
        return result

    # Pause application writers to make source-vs-restored hash comparison meaningful.
    # Only this Compose project's backend is affected; it is always resumed below.
    subprocess.run(["docker", "compose", "pause", "backend"], check=True)
    created = False
    try:
        expected = fingerprint("secureops")
        with dump.open("wb") as output:
            subprocess.run(["docker", "exec", container, "pg_dump", "-U", "secureops", "-d", "secureops", "-Fc"], stdout=output, check=True)
        record["restore_start"] = now()
        subprocess.run(["docker", "exec", container, "createdb", "-U", "secureops", temporary], check=True)
        created = True
        with dump.open("rb") as source:
            subprocess.run(["docker", "exec", "-i", container, "pg_restore", "-U", "secureops", "-d", temporary,
                            "--exit-on-error", "--no-owner"], stdin=source, check=True)
        actual = fingerprint(temporary)
        if not expected or expected != actual:
            raise RuntimeError("Restored data differs from source")
        record.update(validation="passed", restore_completion=now(), tables_verified=sorted(actual),
                      backup_sha256=hashlib.sha256(dump.read_bytes()).hexdigest())
    except Exception:
        record.update(validation="failed", restore_completion=now())
        raise
    finally:
        subprocess.run(["docker", "compose", "unpause", "backend"], check=True)
        if created:
            subprocess.run(["docker", "exec", container, "dropdb", "-U", "secureops", temporary], check=True)
        Path("reports").mkdir(exist_ok=True)
        Path("reports/local-restore.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
