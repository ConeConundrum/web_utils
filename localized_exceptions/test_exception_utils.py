import pytest
from fastapi import status

from localized_exceptions.localized_exception import (
    UserHttpException,
    UserListHttpException
)
from localized_exceptions.utils import (
    UserExceptionTypeEnum,
    UserExceptionSchema, ProductExceptionEnum
)


@pytest.fixture()
def exception_schema():
    return UserExceptionSchema(
        value=status.HTTP_404_NOT_FOUND,
        type=UserExceptionTypeEnum.VALIDATION,
        loc=['category_id'],
        localize=ProductExceptionEnum.NO_PRODUCT.plain_localize
    )


def test_user_exception_handle_localize_correct():
    with pytest.raises(UserHttpException):
        raise UserHttpException(
            status_code=status.HTTP_404_NOT_FOUND,
            value="value",
            exception_type=UserExceptionTypeEnum.VALIDATION,
            error_key=ProductExceptionEnum.NO_PRODUCT
        )


def test_user_exception_list_handle_localize_correct():
    errors = UserListHttpException(status_code=status.HTTP_400_BAD_REQUEST)
    errors.add_detail(
            value=status.HTTP_404_NOT_FOUND,
            exception_type=UserExceptionTypeEnum.VALIDATION,
            loc=['category_id'],
            error_key=ProductExceptionEnum.CATEGORY_NOT_FOUND
    )
    assert errors.get_details()[0].value == status.HTTP_404_NOT_FOUND
    assert errors.get_details()[0].localize["EN"] == "Product category not found"


def test_user_exception_list_merge_details(exception_schema):
    errors = UserListHttpException(status_code=status.HTTP_400_BAD_REQUEST)
    errors.merge_details(
        detail=[exception_schema, exception_schema],
        path_pre="something"
    )
    assert errors.get_details()[0].value == status.HTTP_404_NOT_FOUND
    assert errors.get_details()[0].localize["EN"] == "Product not found"
    assert errors.get_details()[0].loc[0] == "something"
