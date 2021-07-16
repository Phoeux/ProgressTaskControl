import graphene
from graphene_django import DjangoObjectType

from api.models import Tasks, User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class TasksType(DjangoObjectType):
    class Meta:
        model = Tasks


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = User(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class CreateTask(graphene.Mutation):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()
    links = graphene.String()
    progress = graphene.String()

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        links = graphene.String()
        progress = graphene.String()

    def mutate(self, info, title, description, links, progress):
        task = Tasks.objects.create(
            title=title,
            description=description,
            links=links,
            progress=progress)
        return CreateTask(
            id=task.id,
            title=task.title,
            description=task.description,
            links=task.links,
            progress=task.progress
        )


class Query(graphene.ObjectType):
    tasks = graphene.List(TasksType)
    users = graphene.List(UserType)

    def resolve_tasks(self, info, **kwargs):
        return Tasks.objects.all()

    def resolve_users(self, info):
        return User.objects.all()


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
