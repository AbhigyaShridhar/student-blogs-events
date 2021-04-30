from django import forms
from events.models import User, Category, Event, Post
from django.core.files.uploadedfile import InMemoryUploadedFile
from events.humanize import naturalsize
from django_summernote.fields import SummernoteTextFormField

class registerForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ['branch', 'year']

class guestForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ['year']

class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)



class PostForm(forms.Form):
	#restricted = forms.BooleanField()
	content = SummernoteTextFormField()

class Post_Form(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['restricted']

class CategoryForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ['category']


class EventForm(forms.ModelForm):
    max_upload_limit = 6 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    poster = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'poster'

    class Meta:
        model = Event
        fields = ['title', 'description', 'details', 'local','poster']  # Picture is manual

    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('poster')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('poster', "File must be < "+self.max_upload_limit_text+" bytes")

    def save(self, commit=True):
        instance = super(EventForm, self).save(commit=False)

        f = instance.poster   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.poster = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()

        return instance
