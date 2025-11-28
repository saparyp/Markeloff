from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum


class EmailType(str, Enum):
    INFORMATION_REQUEST = "запрос_информации"
    COMPLAINT = "жалоба"
    REGULATORY = "регуляторный"
    PARTNERSHIP = "партнерское_предложение"
    APPROVAL_REQUEST = "согласование"
    NOTIFICATION = "уведомление"


class UrgencyLevel(str, Enum):
    LOW = "низкая"
    MEDIUM = "средняя"
    HIGH = "высокая"
    CRITICAL = "критическая"


class FormalityLevel(str, Enum):
    INFORMAL = "неформальный"
    SEMI_FORMAL = "полуформальный"
    FORMAL = "строго_официальный"


# запрос от фронта
class EmailProcessingRequest(BaseModel):
    email_text: str
    file_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
