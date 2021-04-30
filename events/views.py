from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .SuperMixin import SuperuserRequiredMixin
import markdown2
from django.contrib.auth.decorators import login_required
from .models import User, Post, Comment, Fav, Category, Event, Notification
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView
from .forms import EventForm, registerForm, CommentForm, PostForm, guestForm, Post_Form, CategoryForm
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import BadHeaderError, send_mass_mail

from django.db.models.signals import post_save
from django.dispatch import receiver

class home(OwnerListView):
    model = Post
    template = "events/home.html"

    def get(self, request):
        favorites = []
        notification_count = 0
        notifications = []
        if request.user.is_authenticated:
            rows = request.user.favorite_posts.values('id')
            favorites = [ row['id'] for row in rows ]
            notification_count = Notification.objects.filter(user=request.user).count()
            notifications = Notification.objects.filter(user=request.user)
            if request.user.is_guest:
                posts = Post.objects.filter(restricted=False).order_by('-created_at')
            else:
                posts = Post.objects.all().order_by('-created_at')

        else:
            posts = Post.objects.filter(restricted=False).order_by('-created_at')

        ctx = { 'posts': posts, 'favorites': favorites, 'notifications': notifications, 'notification_count': notification_count }

        return render(request, self.template, ctx)

def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        rollno = request.POST["rollNo"]
        form = registerForm(request.POST)
        if form.is_valid():
            branch = form.cleaned_data['branch']
            year = form.cleaned_data['year']

        else:
            return render(request, "events/register.html", {
                "message": "You didn't provide all the fields",
                "form": registerForm()
            })
        email = str(rollno) + '@iiitu.ac.in'

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "events/register.html", {
                "message": "Passwords must match.",
                "form": registerForm()
            })

        if not username or not rollno or not year or not password or not first_name or not last_name:
            return render(request, "events/register.html", {
                "message": "Please enter all the fields",
                "form": registerForm()
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(first_name, last_name, email, username, year, branch, rollno, password)
            user.set_password(password)

            user.save()
        except IntegrityError:
            return render(request, "events/register.html", {
            "message": "Username already taken.",
            "form": registerForm()
        })
        login(request, user)
        return render(request, 'events/home.html')
    else:
        ctx = { "form": registerForm()}
        return render(request, "events/register.html", ctx)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        rollno = request.POST["rollno"]
        password = request.POST["password"]

        email = rollno + '@iiitu.ac.in'

        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse_lazy("events:home"))
        else:
            return render(request, "events/login.html", {
                "message": "Invalid roll number and/or password."
            })
    else:
        return render(request, "events/login.html")

def guest_register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        college = request.POST["college"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "events/guest_register.html", {
                "message": "Passwords must match.",
                "form": guestForm(),
            })

        if not username or not college or not password or not email:
            return render(request, "events/guest_login.html", {
                "message": "Please enter all the fields",
                "form": guestForm(),
            })

        form = guestForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']

        else:
            return render(request, "events/guest_register.html", {
                "message": "Please enter all the fields",
                "form": guestForm(),
            })

        # Attempt to create new user
        try:
            user = User.objects.create_guest(first_name, last_name, username, college, year, email, password)
            user.set_password(password)
            user.is_guest = True
            user.save()
        except IntegrityError:
            return render(request, "events/guest_register.html", {
            "message": "Username or email is already taken.",
            "form": guestForm(),
        })
        login(request, user)
        return HttpResponseRedirect(reverse("events:home"))
    else:
        ctx = {"form": guestForm()}
        return render(request, "events/guest_register.html", ctx)

def guest_login(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("events:home"))
        else:
            return render(request, "events/guest_login.html", {
                "message": "Invalid roll number and/or password."
            })
    else:
        return render(request, "events/guest_login.html")

def faculty_register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "events/faculty_register.html", {
                "message": "Passwords must match.",
            })

        if not username or not password or not email:
            return render(request, "events/faculty_register.html", {
                "message": "Please enter all the fields",
            })

        if not email.endswith("@iiitu.ac.in"):
            return render(request, "events/faculty_register.html", {
                "message": "Please enter all the fields",
            })

        # Attempt to create new user
        try:
            user = User.objects.create_faculty(first_name, last_name, username, email, password)
            user.set_password(password)
            user.is_faculty = True
            user.save()
        except IntegrityError:
            return render(request, "events/faculty_register.html", {
            "message": "Username or email is already taken.",
        })
        login(request, user)
        return HttpResponseRedirect(reverse("events:home"))
    else:
        return render(request, "events/faculty_register.html")

def faculty_login(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("events:home"))
        else:
            return render(request, "events/faculty_login.html", {
                "message": "Invalid roll number and/or password."
            })
    else:
        return render(request, "events/faculty_login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("events:home"))

class PostDetailView(OwnerDetailView):
    model = Post
    template = "events/post_detail.html"

    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        notifications = []
        tags = post.tagged.all()
        favorites = list()
        notification_count = 0
        if request.user.is_authenticated:
            if request.user.is_guest == True and post.restricted == True:
                return HttpResponseRedirect(reverse("events:home"))
            notification_count = Notification.objects.filter(user=request.user).count()
            notifications = Notification.objects.filter(user=request.user)
        else:
            if post.restricted:
                return HttpResponseRedirect(reverse("events:home"))
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            rows = user.favorite_posts.values('id')
            favorites = [ row['id'] for row in rows ]
        comments = Comment.objects.filter(post=post).order_by('-updated_at')
        comment_form = CommentForm()
        ctx = { 'post': post, 'favorites':favorites, 'comments': comments, 'comment_form': comment_form, 'tags': tags, 'notification_count': notification_count, 'notifications': notifications }
        return render(request, self.template, ctx)

class PostCreateView(OwnerCreateView):
    template = "events/post_form.html"
    success_url = reverse_lazy('events:home')

    def get(self, request):
        form = PostForm()
        postform = Post_Form()
        cform = CategoryForm()
        notifications = []
        notification_count = 0
        if request.user.is_authenticated:
            notification_count = Notification.objects.filter(user=request.user).count()
            notifications = Notification.objects.filter(user=request.user)
        ctx = { 'form': form, 'cform': cform, 'notification_count': notification_count, 'notifications': notifications, 'postform': postform }
        return render(request, self.template, ctx)

    def post(self, request):
        form = PostForm(request.POST)
        cform = CategoryForm(request.POST)
        postform = Post_Form(request.POST)
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["description"]
            tags = request.POST["tag"]
            tusers = tags.split()
            if form.is_valid():
                content = form.cleaned_data["content"]
                post = Post.objects.create(title=title, description=description, content=content, owner=request.user)
                if postform.is_valid():
                    restricted = postform.cleaned_data["restricted"]
                    post.restricted = restricted
                    if cform.is_valid():
                        category = cform.cleaned_data["category"]
                        post.category = category
                        post.save()
                    else:
                        return render(request, self.template, {
                        'form': form,
                        'postform': Post_Form(),
                        'cform': CategoryForm(),
                        'message': "Please Input all the required fields."
                        })
                else:
                    return render(request, self.template, {
                    'form': form,
                    'postform': Post_Form(),
                    'cform': CategoryForm(),
                    'message': "Please Input all the required fields."
                    })
            else:
                return render(request, self.template, {
                'form': form,
                'postform': Post_Form(),
                'cform': CategoryForm(),
                'message': "Please Input all the required fields."
                })

            for us in tusers:
                try:
                    name = User.objects.get(rollNo=us)
                    post.tagged.add(name)
                except User.DoesNotExist:
                    return render(request, self.template, {
                    'form': form,
                    'cform': CategoryForm(),
                    'postform': Post_Form(),
                    'message': "Some or all roll numbers you entered weren't found"
                    })

            post.save()
        return (redirect(self.success_url))

class PostUpdateView(OwnerUpdateView):
    template = 'events/post_form.html'
    success_url = reverse_lazy('events:home')

    def get(self, request, pk):
        pic = get_object_or_404(Post, id=pk, owner=self.request.user)
        form = PostForm(initial={'category': pic.category, 'content': pic.content})
        notifications = []
        notification_count = 0
        if request.user.is_authenticated:
            notification_count = Notification.objects.filter(user=request.user).count()
            notifications = Notification.objects.filter(user=request.user)
        ctx = { 'form': form,
                'title': pic.title,
                'description': pic.description,
                'notification_count': notification_count,
                'notifications': notifications,
                'postform': Post_Form(),
                'cform': CategoryForm()
         }
        return render(request, self.template, ctx)

    def post(self, request, pk):
        pic = get_object_or_404(Post, id=pk, owner=self.request.user)
        form = PostForm(request.POST, initial={'content': pic.content})
        cform = CategoryForm(request.POST, initial={'category': pic.category})

        if not form.is_valid() or not cform.is_valid():
            ctx = { 'form': form,
                'title': pic.title,
                'description': pic.description,
                'cform': CategoryForm()
            }
            return render(request, self.template, ctx)

        title = request.POST["title"]
        description = request.POST["description"]
        tags = request.POST["tag"]
        tusers = tags.strip()
        category = cform.cleaned_data["category"]
        content = form.cleaned_data["content"]

        pic.content = content
        pic.description = description
        pic.category = category
        pic.title = title

        pic.tagged.set([])

        for us in tusers:
                try:
                    name = User.objects.get(rollNo=us)
                    pic.tagged.add(name)
                except User.DoesNotExist:
                    return render(request, self.template, {
                    'form': form,
                    'message': "Some or all roll numbers you entered weren't found"
                })

        pic.save()

        return redirect(self.success_url)

@login_required
def PostDeleteView(request, pk):
    p = Post.objects.get(id=pk)
    p.delete()
    return HttpResponseRedirect(reverse("events:home"))

def stream_file(request, pk):
    event = get_object_or_404(Event, id=pk)
    response = HttpResponse()
    response['Content-Type'] = event.content_type
    response['Content-Length'] = len(event.poster)
    response.write(event.poster)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    model = Comment

    def post(self, request, pk):
        p = get_object_or_404(Post, id=pk)
        com = Comment(text=request.POST['comment'], owner=request.user, post=p)
        com.save()
        p.num_comments = p.num_comments + 1
        p.save()
        return redirect(reverse('events:post_detail', args=[pk]))

@login_required
def CommentDeleteView(request, pk):
    com = Comment.objects.get(id=pk)
    post = Post.objects.get(id=com.post.id)
    post.num_comments = post.num_comments - 1
    post.save()
    post = com.post.id
    com.delete()
    return HttpResponseRedirect(reverse("events:post_detail", kwargs={'pk': post}))

@login_required
@csrf_exempt
def AddFavoriteView(request, pk):
    if request.method == "POST":
        print("Add PK",pk)
        t = get_object_or_404(Post, id=pk)
        t.num_likes = t.num_likes + 1
        t.save()
        fav = Fav(user=request.user, post=t)
        try:
            fav.save()  # In case of duplicate key
        except Post.DoesNotExist:
            pass
        return HttpResponse()

@login_required
@csrf_exempt
def DeleteFavoriteView(request, pk):
    if request.method == "POST":
        print("Delete PK",pk)
        t = get_object_or_404(Post, id=pk)
        t.num_likes = t.num_likes - 1
        t.save()
        try:
            fav = Fav.objects.get(user=request.user, post=t).delete()
        except Post.DoesNotExist:
            pass
        return HttpResponse()

def Profile(request, pk):
    template = 'events/profile.html'
    user = User.objects.get(id=pk)
    posts = Post.objects.filter(owner=user)
    liked_posts = Fav.objects.filter(user=user)
    notifications = []
    notification_count = 0
    if request.user.is_authenticated:
        notification_count = Notification.objects.filter(user=request.user).count()
        notifications = Notification.objects.filter(user=request.user)
    Branch = 'b'
    if user.branch == '1':
        Branch = 'CSE'
    elif user.branch == '2':
        Branch = 'ECE'
    else:
        Branch = 'IT'

    def email_for_gravatar(self):
        return self.user.email

    ctx = {'user': user, 'posts': posts, 'liked_posts': liked_posts, 'Branch': Branch, 'notification_count': notification_count, 'notifications': notifications}
    return render(request, template, ctx)

def events(request):
    template = 'events/events.html'
    events = Event.objects.filter(status=True)
    notification_count = 0
    notifications = []
    if request.user.is_authenticated:
        notification_count = Notification.objects.filter(user=request.user).count()
        notifications = Notification.objects.filter(user=request.user)
        if request.user.is_guest:
            events = Event.objects.filter(status=True, local=False)
    ctx = { 'events': events, 'notification_count': notification_count, 'notifications': notifications }

    return render(request, template, ctx)

class addEvent(SuperuserRequiredMixin, View):
    template = 'events/event_form.html'
    success_url = reverse_lazy('events:events')

    def get(self, request):
        data = { 'details': '### Event Title \nEvent Description..... \n\n## Instructions \n\t1. step 1 \n\t2. step 2 \n.... \n\n## Ending footnote' }
        form = EventForm(initial=data)
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request):
        form = EventForm(request.POST, request.FILES or None)
        pic = form.save(commit=False)
        pic.admin = self.request.user
        if not form.is_valid():
            ctx = { 'form': form }
            return render(request, self.template, ctx)
        category = Category.objects.create(title=pic.title)
        pic.save()
        return redirect(self.success_url)

def event(request, title):
    template = "events/Event.html"
    event = Event.objects.get(title=title)
    entry = event.details
    md = markdown2.Markdown()
    entry = md.convert(entry)
    notification_count = 0
    notifications = []
    if request.user.is_authenticated:
        if request.user.is_guest == True and event.local == True:
            return HttpResponseRedirect(reverse("events:home"))
        notification_count = Notification.objects.filter(user=request.user).count()
        notifications = Notification.objects.filter(user=request.user)
    else:
        if event.local:
            return HttpResponseRedirect(reverse("events:home"))
    ctx = { 'event': event, 'entry': entry, 'notification_count': notification_count, 'notifications': notifications }
    return render(request, template, ctx)

def Eregister(request, title):
    event = Event.objects.get(title=title)
    if not request.user.is_authenticated:
        return render(request, "events/login.html")
    else:
        if request.user.is_guest == True and event.local == True:
            return HttpResponseRedirect(reverse("events:home"))
    if request.user not in event.participants.all():
        event.participants.add(request.user)
        Notification.objects.create(user=request.user, text="You have successfully registered for the event \"" + event.title + "\"")
    else:
        event.participants.remove(request.user)
    return redirect(reverse_lazy('events:events'))

class Edetails(SuperuserRequiredMixin, View):
    template = 'events/details.html'

    def get(self, request, pk):
        event = Event.objects.get(id=pk)
        count = event.participants.count()
        participants = event.participants.all()
        ctx = {
            'count': count,
            'participants': participants,
            'pk': pk
        }
        return render(request, self.template, ctx)

class Ecancel(SuperuserRequiredMixin, View):
    success_url = 'events:events'

    def post(self, request, title):
        event = Event.objects.get(title=title)
        event.delete()
        return HttpResponseRedirect(reverse(self.success_url))

class addc(SuperuserRequiredMixin, View):
    template = 'events/category_form.html'
    success_url = 'events:categories'

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        title = request.POST["title"]
        # Attempt to create new user
        try:
            cat = Category.objects.create(title=title)
            cat.save()
        except IntegrityError:
            return render(request, self.template, {
                "message": "This Category already exists"
            })
        return HttpResponseRedirect(reverse(self.success_url))

def categories(request):
    categories = Category.objects.all()
    template = 'events/categories.html'
    notification_count = 0
    notifications = []
    if request.user.is_authenticated:
        notification_count = Notification.objects.filter(user=request.user).count()
        notifications = Notification.objects.filter(user=request.user)
    ctx = { 'categories': categories, 'notification_count': notification_count, 'notifications': notifications }

    return render(request, template, ctx)

class starred(LoginRequiredMixin, OwnerListView):
    model = Post
    template = "events/home.html"

    def get(self, request):
        favorites = []
        notification_count = 0
        notifications = []
        rows = request.user.favorite_posts.values('id')
        favorites = [ row['id'] for row in rows ]
        notification_count = Notification.objects.filter(user=request.user).count()
        notifications = Notification.objects.filter(user=request.user)
        values = Fav.objects.filter(user = request.user)

        posts = []

        for val in values:
            posts.append(val.post)

        ctx = { 'posts': posts, 'favorites': favorites, 'notifications': notifications, 'notification_count': notification_count }

        return render(request, self.template, ctx)

def category(request, pk):
    cat = Category.objects.get(id=pk)
    template = 'events/home.html'
    favorites = []
    notification_count = 0
    notifications = []
    if request.user.is_authenticated:
        rows = request.user.favorite_posts.values('id')
        favorites = [ row['id'] for row in rows ]
        notification_count = Notification.objects.filter(user=request.user).count()
        notifications = Notification.objects.filter(user=request.user)
        if request.user.is_guest:
            posts = Post.objects.filter(restricted=False, category=cat).order_by('-created_at')
        else:
            posts = Post.objects.filter(category=cat).order_by('-created_at')

    else:
        posts = Post.objects.filter(restricted=False, category=cat).order_by('-created_at')

    ctx = { 'posts': posts, 'favorites': favorites, 'notifications': notifications, 'notification_count': notification_count }

    return render(request, template, ctx)

class send_email(SuperuserRequiredMixin, View):
    template = "events/mail.html"
    success_url = "events/events.html"

    def get(self, request, pk):
        return render(request, self.template, {"pk": pk})

    def post(self, request, pk):
        values=Event.objects.get(id=pk).participants.all()

        if request.user.is_superuser:
            subject = request.POST['subject']
            text = request.POST['message']
            messages = list()
            for val in values:
                message = (subject, text, '19102@iiitu.ac.in', ['19102@iiitu.ac.in', val.email])
                messages.append(message)
            if subject and message:
                try:
                    messages = tuple(messages)
                    send_mass_mail(messages, fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return HttpResponse('emails sent')
            else:
                return HttpResponse('Make sure all fields are entered and valid.')

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Notification.objects.create(user=instance, text='Welcome, ' + instance.first_name + '! Hope You are doing great. Feel free to share something through a casual post, or browse through the active events...')

@receiver(post_save, sender=Fav)
def create_like_notification(sender, instance, created, **kwargs):
	if created:
		Notification.objects.create(user=instance.post.owner, text=instance.user.username + ' liked your post')

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
	if created:
		Notification.objects.create(user=instance.post.owner, text=instance.owner.username + ' commented on your post')

@login_required
def delete_notifications(request):
    n = Notification.objects.filter(user=request.user)
    for notification in n:
        notification.delete()

    return HttpResponseRedirect(reverse("events:home"))
