# Django
from abc import abstractmethod

from django.shortcuts import redirect
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.paginator import Paginator

from django.views import View


# local Django
from .models import Post, Comment
from .forms import RegisterForm, PostForm, CommentForm


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    paginator: Paginator = Paginator(posts, 3)  # Show 3 posts per page
    page = request.GET.get('page')
    if page is None:
        page = 1
    posts = paginator.get_page(page)
    print("paginator.num_pages = ", paginator.num_pages)
    print("paginator.count = ", paginator.count)
    return render(request=request, template_name='blog/post_list.html', context={'posts': posts})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, f"New post created!")
            return redirect('post_list')
        else:
            messages.error(request, "New post was not created!")
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def get_comments(post):
    first_level_comments = post.comments.filter(parent=None)
    res = []
    for comment in first_level_comments:
        replies = get_all_replies_to_comment(comment)
        res += replies
    return res


def get_all_replies_to_comment(comment):
    children = comment.children()
    res = [comment]
    for child in children:
        res += get_all_replies_to_comment(child)
    return res


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments_tree = get_comments(post)
    return render(request, 'blog/post_detail.html', {'post': post, 'comments_tree': comments_tree})


def user_registration(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # validating the password match while creating the user.
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            login(request, user)
            # redirect to a new URL:
            return redirect(reverse('post_list'))
        else:
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
            return render(request=request,
                          template_name="blog/user_registration.html",
                          context={"form": form})
    form = RegisterForm()
    return render(request=request, template_name="blog/user_registration.html", context={"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
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
                messages.info(request, f"You are now logged in as {username}")
                return redirect(reverse('post_list'))
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    form = AuthenticationForm()
    return render(request,
                  "blog/login.html",
                  {"form": form})



class AddCommentOrReplyToPost(View):
    # Do i need here __init__ method?
    form_class = CommentForm
    template_name = 'blog/add_reply_or_comment_to_post.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    # these operations in abstractmethod must be implemented in subclasses.
    @abstractmethod
    def message_success(self):
        pass

    @abstractmethod
    def message_error(self):
        pass

    def get_parent(self):
        return None

    def form_validation(self, form, post):
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = self.request.user
            comment.post = post
            comment.parent = self.get_parent()
            comment.save()
            self.message_success()
            return True
        else:
            self.message_error()
            return False

    """
    Handles POST requests, instantiating a form instance and its inline
    formsets with the passed POST variables and then checking them for
    validity.
    """
    def post_impl(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        form = self.form_class(self.request.POST)
        is_valid = self.form_validation(form, post)
        if is_valid:
            return redirect('post_detail', pk=post.pk)
        else:
            return render(request, self.template_name, {'form': form})


class AddCommentToPost(AddCommentOrReplyToPost):
    # inherit methods from class AddCommentOrReplyToPost()
    def message_success(self):
        messages.success(self.request, f"Comment successfully created!")

    def message_error(self):
        messages.error(self.request, "Comment not created!")

    def post(self, request, pk, *args, **kwargs):
        return self.post_impl(request, pk, *args, **kwargs)


class AddReplyToPost(AddCommentOrReplyToPost):
    # inherit method post from AddCommentOrReplyToPost()
    def message_success(self):
        messages.success(self.request, f"Reply for comment successfully created!")

    def message_error(self):
        messages.error(self.request, "Reply for comment was not created!")

    def get_parent(self):
        return self.parent_comment

    def post(self, request, pk, parent_pk, *args, **kwargs):
        self.parent_comment = get_object_or_404(Comment, pk=parent_pk)
        return self.post_impl(request, pk, *args, **kwargs)

