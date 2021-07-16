import graphene
from graphene_django import DjangoObjectType

from api.models import Tasks


class TasksType(DjangoObjectType):
    class Meta:
        model = Tasks


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
        # task = Tasks(title=title, description=description, links=links, progress=progress)
        # task.save()
        #
        # return CreateTask(
        #     id=task.id,
        #     title=task.title,
        #     description=task.description,
        #     links=task.links,
        #     progress=task.progress
        # )
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

    def resolve_tasks(self, info, **kwargs):
        return Tasks.objects.all()


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()

# schema = graphene.Schema(query=Query, mutation=Mutation)
