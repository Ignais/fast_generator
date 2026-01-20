import logging
import json
from datetime import datetime

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

handler = logging.FileHandler("audit.log", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s | USER=%(user)s | ACTION=%(action)s | DATA=%(data)s"
)
handler.setFormatter(formatter)
audit_logger.addHandler(handler)


def audit(user_id: int, action: str, data: dict):
    audit_logger.info(
        "",
        extra={
            "user": user_id,
            "action": action,
            "data": json.dumps(data, ensure_ascii=False)
        }
    )
