from pydantic import BaseModel, Field
from typing import Optional


class SchemeBase(BaseModel):
	name: str = Field(..., description="唯一标识符名称")
	comment: Optional[str] = Field("", description="注释说明")
