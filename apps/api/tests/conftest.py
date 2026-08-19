import os
import tempfile
from pathlib import Path

TEST_ROOT = Path(tempfile.mkdtemp(prefix="evidence_rag_tests_"))
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
os.environ["AI_PROVIDER"] = "mock"
os.environ["EMBEDDING_DIMENSIONS"] = "256"
os.environ["MIN_EVIDENCE_SCORE"] = "0.12"
