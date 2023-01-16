import pytest

from localized_enum.localized_enum import LocalizedEnum
from localized_enum.utils import LocalizeSchema, EnumObjectSchema


@pytest.fixture()
def localized_enum_class():
    class TestLocalizedEnum(LocalizedEnum):
        ACTIVE = 'ACTIVE', {
            "EN": LocalizeSchema(title='Active'),
            "RU": LocalizeSchema(title='Активный'),
        }
        DELETED = 'DELETED', {
            "EN": LocalizeSchema(title='Deleted'),
            "RU": LocalizeSchema(title='Удалён'),
        }
    return TestLocalizedEnum


def test_localized_enum_class(localized_enum_class):
    assert localized_enum_class.ACTIVE.value == 'ACTIVE'
    assert localized_enum_class.ACTIVE == 'ACTIVE'
    assert isinstance(localized_enum_class.ACTIVE, str)
    assert isinstance(localized_enum_class.ACTIVE, LocalizedEnum)
    for enum_member in localized_enum_class:
        assert isinstance(enum_member, LocalizedEnum)


def test_localize_enum_to_object_list(localized_enum_class):
    enum_len = len(localized_enum_class)
    object_list = localized_enum_class.to_object_list()
    assert enum_len == len(object_list)
    assert isinstance(object_list, list)
    assert isinstance(object_list[0], dict)

    assert object_list[0].get('id') == 0
    assert object_list[0].get('name') == 'ACTIVE'
    assert object_list[0].get('localize')
    assert isinstance(object_list[0].get('localize'), dict)
    assert object_list[0].get('localize').get('EN')


def test_localize_enum_to_schema_list(localized_enum_class):
    schema_list = localized_enum_class.to_schema_list()
    assert isinstance(schema_list, list)
    assert isinstance(schema_list[0], EnumObjectSchema)
    assert schema_list[0].id == 0
    assert schema_list[0].name == 'ACTIVE'
    assert isinstance(schema_list[0].localize, dict)
    assert schema_list[0].localize.get('EN')


def test_localize_enum_member_to_object(localized_enum_class):
    enum_object = localized_enum_class.ACTIVE.enum
    assert isinstance(enum_object, dict)
    assert enum_object.get('id') == 0
    assert enum_object.get('name') == 'ACTIVE'
    assert enum_object.get('localize')


def test_localize_enum_member_to_schema(localized_enum_class):
    enum_schema = localized_enum_class.ACTIVE.schema
    assert isinstance(enum_schema, EnumObjectSchema)
    assert enum_schema.id == 0
    assert enum_schema.name == 'ACTIVE'
    assert isinstance(enum_schema.localize, dict)
    assert enum_schema.localize.get('EN')


def test_create_class_without_localization():
    class TestEnum(LocalizedEnum):
        ACTIVE = 'ACTIVE'
        DELETED = 'DELETED'

    for enum in TestEnum:
        assert TestEnum[enum].enum
        assert TestEnum[enum].schema

    assert TestEnum.to_object_list()
    assert TestEnum.to_schema_list()
