import pytest

from ..argument import Argument
from ..dynamic import Dynamic
from ..fieldresolver import FieldResolver
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema
from ..structures import NonNull


def test_field_resolver_execution():
    class MyFieldResolver(FieldResolver):
        class Arguments:
            name = String()

        name = String()

        def resolve(self, info, name):
            return MyFieldResolver(name=name)

    class Query(ObjectType):
        my_field = MyFieldResolver.Field()

    schema = Schema(query=Query)
    result = schema.execute('''
        query {
            myField(name: "Peter") {
                name
            }
        }
    ''')
    assert not result.errors
    assert result.data == {
        'myField': {
            'name': 'Peter',
        }
    }


def test_field_resolver_no_fields_output():
    class MyFieldResolver(FieldResolver):
        name = String()

        def resolve(self, info):
            return MyFieldResolver()

    class Query(ObjectType):
        my_field = MyFieldResolver.Field()

    schema = Schema(query=Query)
    result = schema.execute('''
        query {
            myField {
                name
            }
        }
    ''')
    assert not result.errors
    assert result.data == {
        'myField': {
            'name': None,
        }
    }


# def test_generate_mutation_no_args():
#     class MyMutation(Mutation):
#         '''Documentation'''

#         def mutate(self, info, **args):
#             return args

#     assert issubclass(MyMutation, ObjectType)
#     assert MyMutation._meta.name == "MyMutation"
#     assert MyMutation._meta.description == "Documentation"
#     resolved = MyMutation.Field().resolver(None, None, name='Peter')
#     assert resolved == {'name': 'Peter'}


# def test_generate_mutation_with_meta():
#     class MyMutation(Mutation):

#         class Meta:
#             name = 'MyOtherMutation'
#             description = 'Documentation'

#         def mutate(self, info, **args):
#             return args

#     assert MyMutation._meta.name == "MyOtherMutation"
#     assert MyMutation._meta.description == "Documentation"
#     resolved = MyMutation.Field().resolver(None, None, name='Peter')
#     assert resolved == {'name': 'Peter'}


# def test_mutation_raises_exception_if_no_mutate():
#     with pytest.raises(AssertionError) as excinfo:

#         class MyMutation(Mutation):
#             pass

#     assert "All mutations must define a mutate method in it" == str(
#         excinfo.value)


# def test_mutation_custom_output_type():
#     class User(ObjectType):
#         name = String()

#     class CreateUser(Mutation):

#         class Arguments:
#             name = String()

#         Output = User

#         def mutate(self, info, name):
#             return User(name=name)

#     field = CreateUser.Field()
#     assert field.type == User
#     assert field.args == {'name': Argument(String)}
#     resolved = field.resolver(None, None, name='Peter')
#     assert isinstance(resolved, User)
#     assert resolved.name == 'Peter'


# def test_mutation_allow_to_have_custom_args():
#     class CreateUser(Mutation):

#         class Arguments:
#             name = String()

#         name = String()

#         def mutate(self, info, name):
#             return CreateUser(name=name)

#     class MyMutation(ObjectType):
#         create_user = CreateUser.Field(
#             description='Create a user',
#             deprecation_reason='Is deprecated',
#             required=True
#         )

#     field = MyMutation._meta.fields['create_user']
#     assert field.description == 'Create a user'
#     assert field.deprecation_reason == 'Is deprecated'
#     assert field.type == NonNull(CreateUser)
