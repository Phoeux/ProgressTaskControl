import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from datetime import date
from dateutil.relativedelta import relativedelta

from api.models import Tasks, User, Links
from api.utils import without_keys


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = '__all__'


class TasksType(DjangoObjectType):
    class Meta:
        model = Tasks
        fields = '__all__'


EnumUserRoles = graphene.Enum.from_enum(User.Role)


class LinksType(DjangoObjectType):
    class Meta:
        model = Links
        fields = '__all__'


class CreateLink(graphene.Mutation):
    link = graphene.Field(LinksType)

    class Arguments:
        url = graphene.String(required=True)

    def mutate(self, info, url):
        if not info.context.user.role == "MANAGER":
            raise Exception("Only Manager can create users")
        link = Links.objects.create(url=url)
        return CreateLink(link=link)


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


class LinksInput(graphene.InputObjectType):
    # id = graphene.ID(requared=True)
    link = graphene.String(requared=True)
    complited = graphene.Boolean()


class CreateTask(graphene.Mutation):
    user = graphene.Field(UserType)
    manager = graphene.Field(UserType)
    task = graphene.Field(TasksType)
    links = graphene.Field(LinksType)

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        links_data = graphene.List(LinksInput)
        user_id = graphene.ID(required=True)
        date_to_check = graphene.Date()

    def mutate(self, info, title, description, links_data, user_id, date_to_check=None):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        if not info.context.user.role == "MANAGER":
            raise Exception("Only Manager can create tasks")
        user = User.objects.get(id=user_id)
        # links = Links.objects.filter(id__in=[val['id'] for val in links_data])
        created_links = []
        for link in links_data:
            links = Links.objects.create(url=link['link'])
            created_links.append(links)
        task = Tasks(
            title=title,
            description=description,
            user=user,
            manager=info.context.user,
            date_to_check=date_to_check
        )
        task.save()
        task.links.set(created_links)
        # task.links.set(links)
        return CreateTask(task=task)


class UpdateTaskInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    links = graphene.List(LinksInput)
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
        if 'links' in upd_data.keys():
            links = Links.objects.filter(id__in=[val['id'] for val in upd_data["links"]])
        if info.context.user.role == "MANAGER":
            if 'links' in upd_data.keys():
                task.links.set(links)
            new_dict = without_keys(upd_data, "links")
            for key, value in new_dict.items():
                setattr(task, key, value)
                task.save()
            return UpdateTask(task=task)
        if info.context.user.role == "USER":
            for data in upd_data['links']:
                if 'complited' in data:
                    links.filter(id=data['id']).update(complited=data['complited'])
            complited_number_of_tasks = task.links.filter(complited=True).count()
            whole_number_of_tasks = task.links.count()
            task.progress = f'{complited_number_of_tasks} out of {whole_number_of_tasks}'
            if whole_number_of_tasks == complited_number_of_tasks:
                task.finished = True
                task.date_to_check = date.today() + relativedelta(months=+3)
        else:
            return Exception(
                ("Don't have permissions! Only manager can edit task. "\
                 "Simple user can edit only links status - complited or not"))
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
    links = graphene.List(LinksType)

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

    def resolve_links(self, info):
        if info.context.user.is_anonymous:
            raise Exception('Not logged in!')
        if info.context.user.role == "MANAGER":
            return Links.objects.all()


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    create_user = CreateUser.Field()
    delete_task = DeleteTask.Field()
    update_task = UpdateTask.Field()
    create_link = CreateLink.Field()
