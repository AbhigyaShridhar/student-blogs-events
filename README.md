# student-blogs-events
This is a blogging and event management platform for students written entirely in django.

## Dependencies
All the dependencies can be checked in the "requirements.txt" file. This project uses python3. 
To install all dependencies perform either "pip3 install -r requirements.txt" or "python3 -m pip install -r requirements.txt"

## Django Markdown
This application allows rendering of rich markdown text to HTML pages using JINJA tags.
In this project, it is used in displaying event details and blogs

## django-crispy-forms
Crispy forms are JINJA tags to automatically provide styling to the forms created and rendered by django.

## django avatar
for creating more personalized profiles, profile pictures can be added by the users. However, storing profile pictures of all the students
will take up a large amount of data. Django-avatar sets the profile picture as the "gravatar" associated with the email address associated
with the user. This saves up space and also sets a uniform profile of the user over various forums as well as this website

## django-summernote
summernote is a rich text editor which allows font styling, links, videos, and image insertion all using it's pre-defined url patterns.
It is added as an app in the "iiitu/settings.py" file.

# Models
All the models can be seen in "events/models.py" file. The default user model is set as "User" which inherits Django's default user class

## Authentication
There are 4 types of users defined through create functions. superuser, user, guest_user and faculty(defined in models.py).
All the user types have different data specifications which is defined in each of their create functions.
To keep the login method of all the users as email, the default authentication back end of django has been edited.
The backend used can be viewed at "events/authentication.py".
## Superusers
There are certain views in the "events/views.py" which should be accessed only by the admin users.
Django provides a LoginRequiredMixin but not for super users. So, in "events/SuperMixin.py", a class is defined which when inheritted by a viwe,
will work only if the user is a superuser. Part of the code has been derived from "Django-Braces" library from pip.

## Humanize
Certain views require the user to upload files (images) and their is a restriction set upon the size of the file. It makes much more sense for an average user
if the requirements are mentioned in MBs or KBs rathers than Bytes. So the "humanize.py" file just contains a function that takes as argument
the size of a file, and returns the size in relavant and understandable format

## Owner class
The main feature of this website is to let users create blogs. Now, their should be an option for the user to edit their blog. To help with this the owner
classes have functions which take instances of models as arguments and return values which reduce the amount of filtering and specification needed to
define in the "views.py" file.

# settings
## summernote and avatar
the summernote text editor version can be specified and for images uploaded via summernote and avatar are to be kept in a directory "media". This directory 
has to be specified as "MEDIA_URL".

## SMTP server
for sending emails to all the participants, the HOST, HOST_USERNAME, and password have to be set up which can be seen in the settings.py file.
Since this file is accessible to the web browser, it is not safe to put the password directly here.

So, the password is kept in "password.txt" file and is read to the HOST_PASSWORD through a file variable. A concept like using an environment variable
for sensitive data such as this.
