from pydantic import BaseModel, Field

class GetQueryPaginatedDTO(BaseModel):
    f: list[str] = None
    s: list[str] = None
    page_no: int = None
    page_size: int = None

