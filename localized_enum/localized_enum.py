from enum import Enum, unique
from typing import Dict, List, Optional

from localized_enum.utils import LocalizeSchema, EnumObjectSchema


@unique
class LocalizedEnum(str, Enum):
    """
    Enum class with typed localization for statuses with auto enumeration
    Need pydantic for localization schemas
    """

    def __new__(cls, *args, **kwargs):
        obj = str.__new__(cls, args[0])
        obj._value_ = args[0]
        obj._obj_id_ = len(cls.__members__)
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(
            self,
            _: str,
            localize: Optional[Dict[str, LocalizeSchema]] = None
    ):
        self._localize_ = None
        self._plain_localize_ = None
        if localize:

            self._localize_ = {
                locale: data.dict()
                for locale, data in localize.items()
            }

            self._plain_localize_ = {
                locale: data.title
                for locale, data in localize.items()
            }

    # overrides for inner methods

    def __str__(self) -> str:
        """enum class method override"""
        return self._value_

    def __hash__(self) -> int:
        """enum class method override"""
        return hash(self._value_)

    def __eq__(self, other) -> bool:
        """enum class method override"""
        return self._value_.__hash__() == other.__hash__()

    # read only parts

    @property
    def localize(self) -> Dict[str, Dict[str, str]]:
        return self._localize_

    @property
    def plain_localize(self) -> Dict[str, str]:
        return self._plain_localize_

    @property
    def object_id(self) -> int:
        return self._obj_id_

    # object converter methods

    @property
    def schema(self) -> EnumObjectSchema:
        return EnumObjectSchema(
            id=self._obj_id_,
            name=self._value_,
            localize=self._localize_
        )

    @property
    def enum(self) -> dict:
        return self.schema.dict()

    # object lists converter methods

    @classmethod
    def to_schema_list(cls) -> List[EnumObjectSchema]:
        return [
            EnumObjectSchema(
                id=obj_id,
                name=key,
                localize=value.__dict__['_localize_']
            )
            for obj_id, (key, value) in enumerate(cls.__members__.items())
        ]

    @classmethod
    def to_object_list(cls) -> List[dict]:
        return [
            {
                'id': obj_id,
                'name': key,
                'localize': value.__dict__['_localize_']
            }
            for obj_id, (key, value) in enumerate(cls.__members__.items())
        ]
