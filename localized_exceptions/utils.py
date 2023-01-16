from enum import unique
from typing import Dict, List, Any

from pydantic import BaseModel

from localized_enum.localized_enum import LocalizedEnum
from localized_enum.utils import LocalizeSchema


@unique
class UserExceptionTypeEnum(LocalizedEnum):
    VALIDATION = 'VALIDATION', {
        "EN": LocalizeSchema(title='Validation error'),
        "RU": LocalizeSchema(title='Ошибка валидации'),
    }
    CRITICAL = 'CRITICAL', {
        "EN": LocalizeSchema(title='Critical error'),
        "RU": LocalizeSchema(title='Критическая ошибка'),
    }


@unique
class ProductExceptionEnum(LocalizedEnum):
    NO_PRODUCT = 'NO_PRODUCT', {
        "EN": LocalizeSchema(title='Product not found'),
        "RU": LocalizeSchema(title='Продукт не найден'),
    }
    CATEGORY_NOT_FOUND = 'CATEGORY_NOT_FOUND', {
        "EN": LocalizeSchema(title='Product category not found'),
        "RU": LocalizeSchema(title='Не найдена категория для продукта'),
    }


class UserExceptionSchema(BaseModel):
    """Schema for user localized errors"""
    value: Any
    type: UserExceptionTypeEnum
    loc: List[Any]  # location of the error by names of model, ex: ['localize', 'EN', 'param']
    localize: Dict[str, str]  # error localization
