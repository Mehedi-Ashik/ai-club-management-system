from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BlogPost, Comment


def post_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    comments = post.comments.all()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
    })


@login_required
def post_create(request):
    if not request.user.is_president:
        messages.error(request, 'You do not have permission!')
        return redirect('blog:list')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        cover_image = request.FILES.get('cover_image')

        BlogPost.objects.create(
            title=title,
            content=content,
            author=request.user,
            cover_image=cover_image,
        )
        messages.success(request, 'Blog post published!')
        return redirect('blog:list')

    return render(request, 'blog/post_create.html')


@login_required
def add_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
            )
            messages.success(request, 'Comment added!')

    return redirect('blog:detail', pk=pk)