import graphene
from blog.schema import QueryBlog,MutationBlog
from users.schema import Query,Mutation
class Query(Query ,QueryBlog,graphene.ObjectType ):
    pass
class Mutation(Mutation,MutationBlog , graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query , mutation=Mutation)