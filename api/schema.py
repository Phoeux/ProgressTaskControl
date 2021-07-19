import graphene
from graphene_django import DjangoObjectType

from api.models import Tasks, User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = '__all__'


class TasksType(DjangoObjectType):
    class Meta:
        model = Tasks

    @classmethod
    def get_queryset(cls, queryset, info):
        """Вывести юзеру только его таски усли не манагер"""
        # if info.context.user.is_anonymous:
        #     return queryset.filter(published=True)
        return queryset


EnumUserRoles = graphene.Enum.from_enum(User.Role)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        role = graphene.Argument(EnumUserRoles)

    def mutate(self, info, username, password, email, role):
        user = User(
            username=username,
            email=email,
            role=role.name
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
    user = graphene.Field(UserType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        links = graphene.String()
        progress = graphene.String()
        user_id = graphene.Int()

    def mutate(self, info, title, description, links, progress, user_id):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        if not info.context.user.role == "MANAGER":
            raise Exception("Only Manager can create tasks")
        user = User.objects.get(id=user_id)

        task = Tasks.objects.create(
            title=title,
            description=description,
            links=links,
            progress=progress,
            user=user
        )
        return CreateTask(
            id=task.id,
            title=task.title,
            description=task.description,
            links=task.links,
            progress=task.progress,
            user=user
        )


class DeleteTask(graphene.Mutation):
    ok = graphene.Boolean()
    task = graphene.Field(TasksType)

    class Arguments:
        id = graphene.ID()

    def mutate(self, info, id):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        if not info.context.user.role == "MANAGER":
            raise Exception("Only Manager can create tasks")
        task = Tasks.objects.get(id=id)
        task.delete()
        return DeleteTask(ok=True, task=task)


class Query(graphene.ObjectType):
    tasks = graphene.List(TasksType)
    users = graphene.List(UserType)
    auth = graphene.Field(UserType)

    def resolve_tasks(self, info, **kwargs):
        return Tasks.objects.all()

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_auth(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        return user


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    create_user = CreateUser.Field()
    delete_task = DeleteTask.Field()

