from django.urls import path, include
from . import views
from django.conf.urls import url

app_name="events"

urlpatterns = [
    path('', views.home.as_view(), name="home"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post/<int:pk>", views.PostDetailView.as_view(), name="post_detail"),
    path("post/create", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/update", views.PostUpdateView.as_view(), name="post_update"),
    path('post/<int:pk>/delete', views.PostDeleteView, name='post_delete'),
    path("post_picture/<int:pk>", views.stream_file, name='post_picture'),
    path("post/<int:pk>/comment", views.CommentCreateView.as_view(), name='post_comment_create'),
    path("comment/<int:pk>/delete", views.CommentDeleteView, name="post_comment_delete"),
    path("add-category", views.addc.as_view(), name="add-category"),
    path("categories", views.categories, name="categories"),
    path("category/<int:pk>", views.category, name="category"),
    path("events", views.events, name="events"),
    path("events/add", views.addEvent.as_view(), name="addEvent"),
    path("Eregister/<str:title>", views.Eregister, name="Eregister"),
    path("Ecancel/<str:title>", views.Ecancel.as_view(), name="Ecancel"),
    path("Edetails<int:pk>", views.Edetails.as_view(), name="Edetails"),
    path("event/<str:title>", views.event, name="event"),
    path("event_poster/<int:pk>", views.stream_file, name="event_poster"),
    path("guest_login", views.guest_login, name="guest_login"),
    path("guest_register", views.guest_register, name="guest_register"),
    path("faculty_login", views.faculty_login, name="faculty_login"),
    path("faculty_register", views.faculty_register, name="faculty_register"),
    path('post/<int:pk>/favorite', views.AddFavoriteView, name='post_favorite'),
    path('post/<int:pk>/unfavorite', views.DeleteFavoriteView, name='post_unfavorite'),
    path('profile/<int:pk>', views.Profile, name="profile"),
    path('starred', views.starred.as_view(), name="starred"),
    path('mail/<int:pk>', views.send_email.as_view(), name='mail'),
    url('avatar/', include('avatar.urls')),

    path('delete_notifications', views.delete_notifications, name='delete_notifications'),


]
