from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404


# Create your views here.
from blog.forms import RegisterForm

from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
# from django.contrib import messages
from .forms import RegisterForm


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request=request, template_name='blog/post_list.html', context={'posts': posts})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            # TODO: add success message
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def user_registration(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            #validating the password match while creating the user.
            username = form.cleaned_data.get('username')
            # messages.success(request, f"New Account Created: {username}")
            raw_pass = form.cleaned_data.get('password')
            login(request,user)
            # redirect to a new URL:
            return redirect(reverse('post_list'))
        # else:
        #     for msg in form.error_messages:
        #         # messages.error(request, f"{msg}: form.error_messages[msg]")
        #     return render(request = request,
        #                   template_name = "blog/user_registration.html",
        #                   context = {"form":form})
    form = RegisterForm()
    return render(request = request,
                          template_name = "blog/user_registration.html",
                          context = {"form":form})




def logout_request(request):
    logout(request)
    # messages.info(request, "Logget out successfully!")
    return redirect(reverse('post_list'))

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # messages.info(request, f"You are now logged in as {username}")
                return redirect(reverse('post_list'))
        #     else:
        #         messages.error(request, "Invalid username or password")
        # else:
        #     messages.error(request, "Invalid username or password")
    
    form = AuthenticationForm()
    return render(request,
                  "blog/login.html",
                  {"form":form})


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})