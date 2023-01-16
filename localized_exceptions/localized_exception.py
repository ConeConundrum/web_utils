from typing import Any, Optional, Dict, List, Union, Type

from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from localized_enum.localized_enum import LocalizedEnum
from localized_exceptions.utils import UserExceptionTypeEnum, UserExceptionSchema


class UserHttpException(HTTPException):
    """
    Class for user localized error
    Raise like common HTTPException
    """
    def __init__(
            self,
            status_code: int,
            value: Any,
            exception_type: UserExceptionTypeEnum,
            error_key: Type[LocalizedEnum],
            loc: Optional[List[Any]] = None,
            headers: Optional[Dict[str, Any]] = None,

    ) -> None:
        detail = UserExceptionSchema(
            value=value,
            type=exception_type,
            loc=loc if loc else list(),
            localize=error_key.plain_localize
        )
        super().__init__(status_code=status_code, detail=jsonable_encoder(detail), headers=headers)


class UserListHttpException(HTTPException):
    """
    Class for user localized errors list with aggregation
    Raise like common exceptions
    """
    def __init__(
            self,
            status_code: int,
            detail: List[UserExceptionSchema] = None,
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.detail = detail if detail else list()

    def add_detail(
            self, *,
            value: Any,
            exception_type: UserExceptionTypeEnum,
            loc: List[Any],
            error_key: Type[LocalizedEnum],
    ) -> None:
        """Add single detail to error stack"""
        self.detail.append(
            UserExceptionSchema(
                value=value,
                type=exception_type,
                loc=loc,
                localize=error_key.plain_localize  # noqa strange ide message for property
            )
        )

    @staticmethod
    def __dict_to_schema(detail: List[dict]):
        return [
            UserExceptionSchema(
                value=record.get('value'),
                type=record.get('type'),
                loc=record.get('loc'),
                localize=record.get('localize')
            ) for record in detail
        ]

    def merge_details(
            self, *,
            detail: Union[List[UserExceptionSchema], List[dict]],
            path_pre: Union[str, list, None] = None,
            path_post: Union[str, list, None] = None
    ) -> None:
        """Merge detail list to error list with option to add path prefix and postfix"""

        if not detail or not isinstance(detail, list):
            return

        # if we get errors from http request they might be dicts
        if all(isinstance(x, dict) for x in detail):
            detail = self.__dict_to_schema(detail=detail)

        if path_pre:
            # add additional path to the beginning of each merged error
            if isinstance(path_pre, str):
                for error in detail:
                    error.loc.insert(0, path_pre)
            if isinstance(path_pre, list):
                for error in detail:
                    error.loc = path_pre + error.loc

        if path_post:
            # add additional path to the end of each merged error
            if isinstance(path_post, str):
                for error in detail:
                    error.loc.append(path_post)
            if isinstance(path_post, list):
                for error in detail:
                    error.loc = error.loc + path_post
        self.detail.extend(detail)

    def get_details(self) -> List[UserExceptionSchema]:
        """Return all details"""
        return self.detail

    def prepare_exception(self) -> Optional[list]:
        """Prepare exception for proper raise"""
        super().__init__(
            status_code=self.status_code,
            detail=jsonable_encoder(self.detail),
            headers=self.headers
        )
        return self.detail
