import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from datetime import date
from dateutil.relativedelta import relativedelta

from api.models import Tasks, User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = '__all__'


class TasksType(DjangoObjectType):
    class Meta:
        model = Tasks
        fields = '__all__'


EnumUserRoles = graphene.Enum.from_enum(User.Role)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        role = graphene.Argument(EnumUserRoles)

    def mutate(self, info, username, password, email, role):
        if not info.context.user.role == "MANAGER":
            raise Exception("Only Manager can create users")
        user = User(
            username=username,
            email=email,
            role=role.name
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class CreateTask(graphene.Mutation):
    user = graphene.Field(UserType)
    manager = graphene.Field(UserType)
    task = graphene.Field(TasksType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        links = graphene.String()
        progress = graphene.String()
        user_id = graphene.ID()

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
            user=user,
            manager=info.context.user
        )
        return CreateTask(task=task)


class UpdateTaskInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    links = graphene.String()
    progress = graphene.String()
    finished = graphene.Boolean()
    user_id = graphene.ID()
    manager_id = graphene.ID()
    passed = graphene.Boolean()


class UpdateTask(graphene.Mutation):
    task = graphene.Field(TasksType)

    class Arguments:
        id = graphene.ID(required=True)
        upd_data = UpdateTaskInput(required=True)

    def mutate(self, info, id, upd_data=None):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        task = Tasks.objects.get(id=id)
        if info.context.user.role == "MANAGER":
            for key, value in upd_data.items():
                setattr(task, key, value)
        elif info.context.user.role == "USER" and 'progress' in upd_data.keys() and len(upd_data) == 1:
            task.progress = upd_data['progress']
        elif info.context.user.role == "USER" and 'finished' in upd_data.keys() and len(upd_data) == 1:
            task.finished = upd_data['finished']
            if task.finished:
                task.date_to_check = date.today() + relativedelta(months=+3)
        elif info.context.user.role == "USER" and 'progress' in upd_data.keys() and 'finished' in upd_data.keys() and \
                len(upd_data) == 2:
            task.progress = upd_data['progress']
            task.finished = upd_data['finished']
            if task.finished:
                task.date_to_check = date.today() + relativedelta(months=+3)
        else:
            return Exception(
                "Don't have permissions! Only manager can edit task. Simple user can edit only his progress")
        task.save()
        return UpdateTask(task=task)


class DeleteTask(graphene.Mutation):
    ok = graphene.Boolean()
    task = graphene.Field(TasksType)

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        if not info.context.user.role == "MANAGER":
            raise Exception("Only Manager can create tasks")
        task = Tasks.objects.get(id=id)
        task.delete()
        return DeleteTask(ok=True, task=task)


class Query(graphene.ObjectType):
    tasks = graphene.List(TasksType, search=graphene.String())
    users = graphene.List(UserType)
    auth = graphene.Field(UserType)

    def resolve_tasks(self, info, search=None, **kwargs):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        if info.context.user.role == "MANAGER":
            if search:
                filter = (Q(user__username__icontains=search))
                return Tasks.objects.filter(filter)
            return Tasks.objects.all()
        if info.context.user.role == "USER":
            return Tasks.objects.filter(user=info.context.user)

    def resolve_users(self, info):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
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
    update_task = UpdateTask.Field()
