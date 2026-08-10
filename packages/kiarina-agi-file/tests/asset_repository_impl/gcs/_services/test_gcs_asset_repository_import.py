import subprocess
import sys


def test_import_error_suggests_gcs_extra() -> None:
    script = """
import sys

sys.modules["google.cloud.exceptions"] = None
sys.modules["google.cloud.storage"] = None

from kiarina.agi.asset_repository_impl.gcs._services import (
    gcs_asset_repository,
)
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "pip install 'kiarina-agi-file[asset-repository-gcs]'" in result.stderr
