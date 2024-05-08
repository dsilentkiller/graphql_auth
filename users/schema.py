import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import create_refresh_token, get_token
from graphql_jwt.decorators import login_required


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        User = get_user_model()  # get user model
        user = User.objects.create_user(  # corrected way to create user
            username=username,
            email=email,
            password=password,
        )
        # user.set_password(password)
        user.save()
        token = get_token(user)  # generate token
        refresh_token = create_refresh_token(user)  # genertae refresh token

        return CreateUser(user=user, token=token, refresh_token=refresh_token)


class Query(graphene.ObjectType):
    whoami = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_whoami(self, info):
        user = info.context.user

        # check user authenticate

        if user.is_anonymous:
            raise Exception('Authentication Failure:You must be signed in')
        return user

    # check user is authenticated using decorator
    @login_required
    def resolve_users(self, info):
        return get_user_model().objects.all()


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
