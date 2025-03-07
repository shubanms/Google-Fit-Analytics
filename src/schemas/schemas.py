from pydantic import BaseModel
from typing import List, Optional


class DataDigestResponse(BaseModel):
    message: str
    process_time_sec: float
    row_count: int
    columns: List[str]

class DataDigestError(BaseModel):
    message: str
    error: str
