from ..field import Field
from ..interface import Interface
from ..objecttype import ObjectType
from ..unmountedtype import UnmountedType
from ..scalars import String
from ..schema import Schema


class MyType(object):
    pass


class MyScalar(UnmountedType):

    def get_type(self):
        return MyType


def test_generate_interface():
    class MyInterface(Interface):
        '''Documentation'''

    assert MyInterface._meta.name == "MyInterface"
    assert MyInterface._meta.description == "Documentation"
    assert MyInterface._meta.fields == {}


def test_generate_interface_with_meta():
    class MyInterface(Interface):

        class Meta:
            name = 'MyOtherInterface'
            description = 'Documentation'

    assert MyInterface._meta.name == "MyOtherInterface"
    assert MyInterface._meta.description == "Documentation"


def test_generate_interface_with_fields():
    class MyInterface(Interface):
        field = Field(MyType)

    assert 'field' in MyInterface._meta.fields


def test_ordered_fields_in_interface():
    class MyInterface(Interface):
        b = Field(MyType)
        a = Field(MyType)
        field = MyScalar()
        asa = Field(MyType)

    assert list(MyInterface._meta.fields.keys()) == ['b', 'a', 'field', 'asa']


def test_generate_interface_unmountedtype():
    class MyInterface(Interface):
        field = MyScalar()

    assert 'field' in MyInterface._meta.fields
    assert isinstance(MyInterface._meta.fields['field'], Field)


def test_generate_interface_inherit_abstracttype():
    class MyAbstractType(object):
        field1 = MyScalar()

    class MyInterface(Interface, MyAbstractType):
        field2 = MyScalar()

    assert list(MyInterface._meta.fields.keys()) == ['field1', 'field2']
    assert [type(x) for x in MyInterface._meta.fields.values()] == [Field, Field]


def test_generate_interface_inherit_interface():
    class MyBaseInterface(Interface):
        field1 = MyScalar()

    class MyInterface(MyBaseInterface):
        field2 = MyScalar()

    assert MyInterface._meta.name == 'MyInterface'
    assert list(MyInterface._meta.fields.keys()) == ['field1', 'field2']
    assert [type(x) for x in MyInterface._meta.fields.values()] == [Field, Field]


def test_generate_interface_inherit_abstracttype_reversed():
    class MyAbstractType(object):
        field1 = MyScalar()

    class MyInterface(MyAbstractType, Interface):
        field2 = MyScalar()

    assert list(MyInterface._meta.fields.keys()) == ['field1', 'field2']
    assert [type(x) for x in MyInterface._meta.fields.values()] == [Field, Field]


def test_allow_custom_resolve_type_func():
    def character_type_resolver(instance, info):
        if instance['type'] == 'Human':
            return Human
        raise NotImplementedError('Unrecognised type')

    class Character(Interface):
        class Meta:
            type_resolver = character_type_resolver

        name = String()

        def resolve_name(root, info):
            return root['name']

    class Human(ObjectType):
        class Meta:
            interfaces = (Character,)

    class Query(ObjectType):
        main_character = Field(Character)

        def resolve_main_character(self, info):
            return {
                'type': 'Human',
                'name': 'Luke Skywalker',
            }

    schema = Schema(query=Query, types=[
        Human,
    ])
    result = schema.execute(''' query basequery {
        mainCharacter {
            name
        }
    }
    ''')
    assert not result.errors
    assert result.data == {
        'mainCharacter': {
            'name': 'Luke Skywalker',
        }
    }
