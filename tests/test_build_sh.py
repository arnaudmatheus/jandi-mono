"""build.sh fails when any of its parallel tasks fails."""

import os
import subprocess

from conftest import REPO

FAILING_PYTHON = REPO / "tests" / "fakes" / "failing_python"


def test_a_failed_merge_fails_the_build():
    # Regression: the tasks ran in the background and a bare `wait` always
    # returned 0, so a crashed merge.py still printed a "successful" build.
    env = dict(os.environ, FAMILIES="normal", STYLES="Regular", JOBS="1")
    run = subprocess.run(
        [REPO / "build.sh", FAILING_PYTHON], env=env, capture_output=True, text=True
    )
    assert run.returncode == 1
    assert "a task failed" in run.stderr
