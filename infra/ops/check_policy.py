from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

OPS_DIR = Path(__file__).resolve().parent
WRAPPER = OPS_DIR / "evidence-rag-ops"
SUDOERS = OPS_DIR / "evidence-rag.sudoers"
REPO_ROOT = OPS_DIR.parents[1]

ACTIONS = {
    "config",
    "status",
    "logs",
    "health",
    "tests",
    "build",
    "deploy",
    "seed-public",
    "smoke",
    "restart",
    "rollback",
}
PINNED_FILES = {
    "COMPOSE_SHA256": "compose.yaml",
    "PROD_COMPOSE_SHA256": "compose.prod.yaml",
    "API_DOCKERFILE_SHA256": "apps/api/Dockerfile",
    "WEB_DOCKERFILE_SHA256": "apps/web/Dockerfile",
}


def fail(message: str) -> None:
    raise SystemExit(f"POLICY CHECK FAILED: {message}")


def main() -> int:
    wrapper = WRAPPER.read_text(encoding="utf-8")
    sudoers = SUDOERS.read_text(encoding="utf-8")

    subprocess.run(["/bin/bash", "-n", str(WRAPPER)], check=True)
    subprocess.run(["/usr/sbin/visudo", "-cf", str(SUDOERS)], check=True)

    if WRAPPER.stat().st_mode & 0o002:
        fail("el wrapper fuente no puede ser escribible por otros")

    for forbidden in (
        "docker system prune",
        "docker volume rm",
        "docker container prune",
        "docker image prune",
        "compose down",
        "down -v",
        "docker exec",
        "eval ",
    ):
        if forbidden in wrapper:
            fail(f"operación prohibida presente: {forbidden!r}")

    for required in (
        "#!/bin/bash -p",
        "--host unix:///var/run/docker.sock",
        "--project-name evidence-rag",
        "--network none",
        "git@github.com:InnerRam/evidence-rag.git",
        "core.hooksPath=/dev/null",
        "merge-base --is-ancestor",
        "merge --ff-only",
    ):
        if required not in wrapper:
            fail(f"control requerido ausente: {required!r}")

    smoke_match = re.search(
        r"exec -T api python3 - <<'PY'\n(?P<code>.*?)\nPY\n",
        wrapper,
        flags=re.DOTALL,
    )
    if not smoke_match:
        fail("smoke embebido ausente")
    compile(smoke_match.group("code"), str(WRAPPER), "exec")

    for action in ACTIONS:
        exact = f"/usr/local/sbin/evidence-rag-ops {action}"
        if sudoers.count(exact) != 1:
            fail(
                "la regla sudoers debe contener exactamente "
                f"una entrada para {action}"
            )

    sudo_commands = set(
        re.findall(r"/usr/local/sbin/evidence-rag-ops ([a-z-]+)", sudoers)
    )
    if sudo_commands != ACTIONS:
        fail(f"acciones sudoers inesperadas: {sorted(sudo_commands ^ ACTIONS)}")

    for variable, relative in PINNED_FILES.items():
        match = re.search(rf'readonly {variable}="([0-9a-f]{{64}})"', wrapper)
        if not match:
            fail(f"hash fijado ausente: {variable}")
        actual = hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()
        if match.group(1) != actual:
            fail(f"hash desactualizado para {relative}")

    print(
        "POLICY OK | bash=valid | sudoers=valid | smoke=valid | actions=11 "
        "| operational-files=pinned | destructive-docker=absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
