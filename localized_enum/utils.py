from typing import Optional, Dict, Union

from pydantic import BaseModel, NonNegativeInt


class LocalizeSchema(BaseModel):
    """Localization object schema"""
    title: str
    short_title: Optional[str] = None
    symbol: Optional[str] = None
    code: Optional[str] = None


class EnumObjectSchema(BaseModel):
    """Enum object schema"""
    id: NonNegativeInt
    name: str
    localize: Optional[Dict[str, Union[LocalizeSchema, str]]] = None
