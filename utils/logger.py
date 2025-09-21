import logging, sys

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    encoding="utf-8"  # ✅ ensures emoji support
)

logger = logging.getLogger("OmniAI")