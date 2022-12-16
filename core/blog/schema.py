import graphene
from graphene import relay,ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField #neednot resolve
from blog import models
from graphql_relay.node.node import from_global_id
from django.contrib.auth.mixins import LoginRequiredMixin


class ProfileType(DjangoObjectType):
    class Meta:
        model = models.Profile
        interfaces = (relay.Node, )
        filter_fields=["user"]


class PostType(DjangoObjectType):
    class Meta:
        model = models.Post
        interfaces = (relay.Node, )
        filter_fields = ['title', 'tags']

class TagType(DjangoObjectType):
    class Meta:
        model = models.Tag
        interfaces = (relay.Node, )
        filter_fields = ['name',]



class QueryBlog(ObjectType):
    profile=relay.Node.Field(ProfileType)
    all_profiles=DjangoFilterConnectionField(ProfileType)
    post=relay.Node.Field(PostType)
    all_posts=DjangoFilterConnectionField(PostType)
    tag=relay.Node.Field(TagType)
    all_tags=DjangoFilterConnectionField(TagType)

class PostMutation(LoginRequiredMixin,relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        subtitle = graphene.String()
        body = graphene.String(required=True)
        meta_description = graphene.String()

        tags = graphene.String(required=True)

    post = graphene.Field(PostType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        title=kwargs.get("title")
        body=kwargs.get("body")
        tags=kwargs.get("tags")
        subtitle=kwargs.get("subtitle" , None)
        author=info.context.user.profile
        tag=None
        if models.Tag.objects.filter(name=tags).exists():
            tag=models.Tag.objects.get(name=tags)
        else:
            tag=models.Tag.objects.create(name=tags)
            tag.save()
        post=models.Post.objects.create(
            title=title,
            body=body,
            author=author,
            tags=tag,
        )

        post.tags=tag
        if subtitle:
            post.subtitle=subtitle
        post.save()

        return PostMutation(post=post)


class PostMutationUpdate(relay.ClientIDMutation):
    class Input:
        id=graphene.String()
        title = graphene.String()
        subtitle = graphene.String()
        body = graphene.String()
        meta_description = graphene.String()

        tags = graphene.String()

    post = graphene.Field(PostType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        id =from_global_id(kwargs['id'])[1]
        post=models.Post.objects.get(id=id)
        if info.context.user != post.author.user:
            raise Exception(" you are not authorized")
        if "title" in kwargs:
            post.title=kwargs['title']
        if 'tags' in kwargs:
            if models.Tag.objects.filter(name=kwargs["tags"]):
                post.tags=models.Tag.objects.get(name=kwargs["tags"])
            else:
                tag=models.Tag.objects.create(name=kwargs["tags"])
                tag.save()
                post.tags=tag
        if "body" in kwargs:
            post.body=kwargs["body"]
        if "subtitle" in kwargs:
            post.subtitle=kwargs["subtitle"]
        if "meta_description" in kwargs:
            post.meta_description=kwargs["meta_description"]

        post.save()


        return PostMutationUpdate(post=post)
class PostMutationDelete(relay.ClientIDMutation):
    class Input:
        id=graphene.String()

    ok=graphene.Boolean()
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        id=from_global_id(kwargs["id"])[1]
        obj=models.Post.objects.get(id=id)
        print(info.context.user ,obj.author.user )
        if info.context.user != obj.author.user:
            raise Exception(" you are not authorized")
        obj.delete()
        return cls(ok=True)



class ProfileMutation(LoginRequiredMixin,relay.ClientIDMutation):
    class Input:
        bio = graphene.String()
        website = graphene.String()

    profile = graphene.Field(ProfileType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user=info.context.user
        if models.Profile.objects.filter(user=user).exists():
            raise Exception(" alredy has an profile")

        profile=models.Profile.objects.create(user=user)

        website=kwargs.get("website" , None)
        bio=kwargs.get("bio" , None)
        if website:
            profile.website=website
        if bio:
            profile.bio=bio
        profile.save()
        return ProfileMutation(profile=profile)
class ProfileMutationUpdate(LoginRequiredMixin,relay.ClientIDMutation):
    class Input:
        id=graphene.String()
        bio = graphene.String()
        website = graphene.String()

    profile = graphene.Field(ProfileType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        id=from_global_id(kwargs["id"])[1]
        profile=models.Profile.objects.get(id=id)
        if info.context.user !=profile.user:
            raise Exception(" not allowed ")
        website=kwargs.get("website" , None)
        bio=kwargs.get("bio" , None)
        if website:
            profile.website=website
        if bio:
            profile.bio=bio
        profile.save()

        return ProfileMutation(profile=profile)
class profileMutationDelete(relay.ClientIDMutation):
    class Input:
        id=graphene.String()

    ok=graphene.Boolean()
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        id=from_global_id(kwargs["id"])[1]
        obj=models.Profile.objects.get(id=id)
        if info.context.user != obj.user:
            raise Exception(" you are not authorized")
        obj.delete()
        return cls(ok=True)

class QueryBlog(ObjectType):
    profile=relay.Node.Field(ProfileType)
    all_profiles=DjangoFilterConnectionField(ProfileType)
    post=relay.Node.Field(PostType)
    all_posts=DjangoFilterConnectionField(PostType)
    tag=relay.Node.Field(TagType)
    all_tags=DjangoFilterConnectionField(TagType)

class MutationBlog(graphene.ObjectType):
    create_post = PostMutation.Field()
    update_post=PostMutationUpdate.Field()
    delete_post=PostMutationDelete.Field()
    create_profile=ProfileMutation.Field()
    update_profile=ProfileMutationUpdate.Field()
    delete_profile=profileMutationDelete.Field()

