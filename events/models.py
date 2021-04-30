from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, username, year, branch, rollNo, password=None):
        if not email:
            raise ValueError("Users must have an email")
        if not username:
            raise ValueError("Users must have a username")
        if not year:
            raise ValueError("Users must specify an year")
        if not branch:
            raise ValueError("Users must specify a branch")
        if not rollNo:
            raise ValueError("Users must have a roll number")
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")

        user = self.model(
                first_name=first_name,
                last_name=last_name,
                email=self.normalize_email(email),
                username=username,
                year=year,
                branch=branch,
                rollNo=rollNo
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_guest(self, first_name, last_name, username, college, year, email, password=None):
        if not username:
            raise ValueError("Please give a valid username")
        if not college:
            raise ValueError("Please provide your college")
        if not year:
            raise ValueError("Specify your year")
        if not email:
            raise  ValueError("A valid email needs to be provided")
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")

        user = self.model(
                first_name=first_name,
                last_name=last_name,
                email = self.normalize_email(email),
                username = username,
                year = year,
                college = college
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_faculty(self, first_name, last_name, username, email, password=None):
        if not username:
            raise ValueError("Please give a valid username")
        if not email:
            raise  ValueError("A valid email needs to be provided")
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")

        user = self.model(
                first_name=first_name,
                last_name=last_name,
                email = self.normalize_email(email),
                username = username,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, year, branch, rollNo, password):
        user = self.model(
                first_name=first_name,
                last_name=last_name,
                email=self.normalize_email(email),
                username=username,
                year=year,
                branch=branch,
                rollNo=rollNo,
                password=password
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    college = models.CharField(blank=True, max_length=60, default="Indian Institute of Information Technology, Una")
    first = 1
    second = 2
    third = 3
    fourth = 4
    YEAR_CHOICES = (
        (first, 'first'),
        (second, 'second'),
        (third, 'third'),
        (fourth, 'fourth')
    )
    year = models.IntegerField(choices=YEAR_CHOICES, default=2)
    Branch_CHOICES = (
        ('1', 'CSE'),
        ('2', 'ECE'),
        ('3', 'IT')
    )
    branch = models.CharField(max_length=3, choices=Branch_CHOICES, default="CSE")
    rollNo = models.CharField(validators=[MinLengthValidator(5)], max_length=5, blank=True)

    profile_pic = models.ImageField(blank=True, null=True, editable=True, upload_to="profile_image")
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'year', 'branch', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.rollNo + " - " + self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

DEFAULT_ID = 1

class Post(models.Model):
    restricted = models.BooleanField(default=False)
    title = models.CharField(
            max_length=100,
            validators=[MinLengthValidator(3, "Title must be greater than 3 characters")]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=DEFAULT_ID)
    restricted = models.BooleanField(default=False)
    description = models.CharField(max_length=200,
        validators=[MinLengthValidator(20, "Description must be greater than 20 characters")]
        )
    tagged = models.ManyToManyField(User, default=None, related_name='tagged_users', null=True, blank=True)
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.ManyToManyField(User,
        through='Comment', related_name='comments_owned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Favorites
    favorites = models.ManyToManyField(User,
        through='Fav', related_name='favorite_posts')
    num_likes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')

    # Shows up in the admin list
    def __str__(self):
        return self.title

class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'

class Fav(models.Model) :
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('post', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.post.title[:10])

class Event(models.Model):
    local = models.BooleanField(default=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    participants = models.ManyToManyField(User, related_name="registered")
    status = models.BooleanField(default=True)
    details = models.TextField(blank=False)
    description = models.CharField(max_length=200)
    poster = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')
    restricted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="notifications")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
