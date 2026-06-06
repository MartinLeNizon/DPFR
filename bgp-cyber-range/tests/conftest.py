import os
import subprocess

import pytest

_CMD = os.environ.get("CONTAINER_CMD", "docker")

CONTAINERS = {
    "main":    "router-main-as100",
    "branch":  "router-branch-as200",
    "transit": "router-transit-as300",
    "rogue":   "router-rogue-as666",
}


def _exec(container: str, *args: str, timeout: int = 30) -> str:
    r = subprocess.run(
        [_CMD, "exec", container, *args],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.stdout + r.stderr


@pytest.fixture(scope="session")
def require_containers():
    r = subprocess.run(
        [_CMD, "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=10,
    )
    running = set(r.stdout.splitlines())
    missing = [name for name in CONTAINERS.values() if name not in running]
    if missing:
        pytest.fail(
            f"Required containers are not running: {missing}\n"
            f"Start the range first:  docker-compose up -d"
        )


@pytest.fixture(scope="session")
def main(require_containers):
    return lambda *args, **kw: _exec(CONTAINERS["main"], *args, **kw)


@pytest.fixture(scope="session")
def branch(require_containers):
    return lambda *args, **kw: _exec(CONTAINERS["branch"], *args, **kw)


@pytest.fixture(scope="session")
def transit(require_containers):
    return lambda *args, **kw: _exec(CONTAINERS["transit"], *args, **kw)
