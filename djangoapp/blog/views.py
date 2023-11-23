
from typing import Any

from blog.models import Page, Post
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView

PER_PAGE = 9


class PostListView(ListView):
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()  # type: ignore

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Home - ',
        })
        return context


def created_by(request, author_pk):
    user = User.objects.filter(pk=author_pk).first()
    if user is None:
        raise Http404()

    posts = (
        Post.
        objects.
        get_published().filter(created_by__pk=author_pk)  # type:ignore
    )
    user_full_name = user.username

    if user.first_name:
        user_full_name = f'{user.first_name} {user.last_name}'

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)
    page_title = user_full_name + ' posts - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'posts': posts,
            'page_title': f'{page_title} - ',
        }
    )


class CreatedByListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_context: dict[str, Any] = {}

    def get(self, request, *args, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            raise Http404()

        self._temp_context.update({
            'author_pk': author_pk,
            'user': user,
        })
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self._temp_context['user']
        user_full_name = user.username

        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'

        page_title = user_full_name + ' posts - '

        ctx.update({
            'page_title': page_title
        })

        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self.kwargs.get('author_pk'))
        return qs


class CategoryListView(PostListView):
    allow_empty = False

    def get_context_data(self, **kwargs):
        ctx_super = super().get_context_data(**kwargs)
        page_title = (
            f'Categoria - {self.object_list[0].category.name} - '  # type: ignore
        )
        ctx_super.update({
            'page_title': page_title
        })
        return ctx_super

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(category__slug=self.kwargs.get('slug'))
        )
        return qs


class TagListView(PostListView):
    allow_empty = False

    def get_context_data(self, **kwargs):
        ctx_super = super().get_context_data(**kwargs)
        filtered_tag = (
            self.object_list[0].tags
            .filter(slug=self.kwargs.get('slug')).first().name
        )
        page_title = (
            f'Tag - {filtered_tag} - '  # type: ignore
        )
        ctx_super.update({
            'page_title': page_title
        })
        return ctx_super

    def get_queryset(self):
        return (
            super().get_queryset().filter(tags__slug=self.kwargs.get('slug'))
        )


def search(request):
    search_value = request.GET.get('search', '').strip()
    posts = (
        Post.objects.get_published().filter(  # type:ignore ;
            Q(title__icontains=search_value) |
            Q(excerpt__icontains=search_value) |
            Q(content__icontains=search_value)
        )[0:PER_PAGE]
    )

    page_title = f'Search - {search_value[:30]} - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'posts': posts,
            'search_value': search_value,
            'page_title': page_title,
        }
    )


def page(request, slug):

    posts = (
        Page.objects.get_published()  # type:ignore
        .filter(slug=slug)
        .first()
    )

    if posts is None:
        raise Http404()

    page_title = f'Página - {posts.title} - '

    return render(
        request,
        'blog/pages/page.html',
        {
            'page': posts,
            'page_title': page_title,
        }
    )


def post(request, slug):
    post_obj = (
        Post.objects.get_published()  # type:ignore
        .filter(slug=slug)
        .first()
    )

    if post_obj is None:
        raise Http404()

    page_title = f'Post - {post_obj.title} - '

    return render(
        request,
        'blog/pages/post.html',
        {
            'post': post_obj,
            'page_title': page_title,
        }
    )
