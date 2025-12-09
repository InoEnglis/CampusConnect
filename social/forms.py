from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from .models import EventReminder, Feedback, GroupJoinRequest, GroupRule, Post, Comment, Group, UserProfile
from django.contrib.auth.models import User
from .models import Event, EventImage, EventFile
from datetime import timedelta
from django.utils import timezone



class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'extension',
            'birth_date',
            'province',
            'municipality',
            'barangay',
            'street',
            'current_work',
            'section',
            'year_level',
            'course',
            'department',
        ]
        widgets = {
            'birth_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': (timezone.now() - timedelta(days=365*12)).strftime('%Y-%m-%d'),
                }
            ),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        today = timezone.now().date()

        if not birth_date:
            return birth_date  # let required field logic handle this if applicable

        if birth_date >= today:
            raise forms.ValidationError("Birth date cannot be today or in the future.")

        # Calculate age (but don't block submission)
        min_birth_date = today.replace(year=today.year - 12)
        if birth_date > min_birth_date:
            # This will show as a warning but still allow submission
            self.add_warning(
                'birth_date',
                "Warning: You appear to be under 12 years old. If this is incorrect, please correct your birth date."
            )
        return birth_date

    def add_warning(self, field, message):
        """
        Add a warning message to a field without making the form invalid
        """
        if not hasattr(self, '_warning_messages'):
            self._warning_messages = {}
        self._warning_messages[field] = message





class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='', 
        widget=forms.Textarea(attrs={
            'placeholder': 'Share your thoughts...', 
            'class': 'form-control form-control-lg', 
            'rows': 3, 
        })
    )

    image = forms.ImageField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',  
            'aria-label': 'Upload an image',
            'class': 'form-control-file', 
        })
    )

    video = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={
            'accept': 'video/*', 
            'aria-label': 'Upload a video',
            'class': 'form-control-file',
        })
    )

    class Meta:
        model = Post
        fields = ['body', 'image', 'video']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Field('body', css_class='form-control form-control-lg'),
            Field('image', css_class='form-control-file mb-4'),
            Field('video', css_class='form-control-file mb-4'),  
            Submit('submit', 'Post', css_class='btn btn-success btn-block')
        )



class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'placeholder': 'Write a comment...',  
            'class': 'form-control form-control-lg',
            'rows': 3, 
        })
    )

    class Meta:
        model = Comment
        fields = ['comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Field('comment', css_class='form-control form-control-lg'),
            Submit('submit', 'Comment', css_class='btn btn-primary btn-block')
        )


from django import forms
from .models import Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Group Name',  
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the group name',  
            'class': 'form-control form-control-lg', 
        })
    )

    description = forms.CharField(
        label='Group Description', 
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe your group...',  
            'class': 'form-control form-control-lg',
            'rows': 4,  
        })
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file', 
        })
    )

    is_private = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'aria-label': 'Private Group', 
        })
    )

    banner_color = forms.CharField(
        label='Group Banner Color', 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '#FFFFFF (Hex color code)',  # Suggesting Hex color format
            'class': 'form-control form-control-lg', 
        })
    )

    class Meta:
        model = Group
        fields = ['name', 'description', 'profile_image', 'is_private', 'banner_color']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # Store user in the form instance

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('name', css_class='form-control form-control-lg'),
                Field('description', css_class='form-control form-control-lg'),
                Field('profile_image', css_class='form-control-file mb-4'),
                Field('is_private', css_class='form-check-input'),
                Field('banner_color', css_class='form-control form-control-lg'),  # Add banner color field
                Submit('submit', 'Save Changes', css_class='btn btn-primary btn-block')
            )
        )
    
    def save(self, commit=True):
        group = super().save(commit=False)
        group.creator = self.user  # Assign the current logged-in user as the creator
        
        if commit:
            group.save()
            group.admins.add(group.creator)  # Add creator as an admin
            group.members.add(group.creator)  # Add creator as a member
        
        return group

class AdminManagementForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User to Make Admin")

class JoinRequestApprovalForm(forms.ModelForm):
    class Meta:
        model = GroupJoinRequest
        fields = ['status']
        
class PostApprovalForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['post_approval_required']

    
    
    

from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['file']

class CSVUploadForm(forms.Form):
     csv_file = forms.FileField(required=True, label="CSV File", help_text="Upload a CSV file to import users.")


from .models import Report
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'additional_comments']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Select a reason',
            }),
            'additional_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide additional details (optional)',
            }),
        }

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if reason not in dict(Report.REASON_CHOICES):
            raise forms.ValidationError("Invalid reason selected.")
        return reason

    def clean_additional_comments(self):
        additional_comments = self.cleaned_data.get('additional_comments')
        if additional_comments and len(additional_comments) > 500:
            raise forms.ValidationError("Additional comments cannot exceed 500 characters.")
        return additional_comments



class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'location_type', 'department', 'building', 'room_number', 
                  'province', 'municipality', 'barangay', 'specific_location', 'images', 'video', 'files', 'video_file','registration_link']
    
    images = forms.ModelMultipleChoiceField(
        queryset=EventImage.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    files = forms.ModelMultipleChoiceField(
        queryset=EventFile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    video = forms.URLField(required=False)
    video_file = forms.FileField(required=False)
    
    location_type = forms.ChoiceField(choices=Event.LOCATION_CHOICES, required=True)

    # Conditionally required fields
    department = forms.CharField(max_length=255, required=False)
    building = forms.CharField(max_length=255, required=False)
    room_number = forms.CharField(max_length=255, required=False)

    province = forms.CharField(max_length=255, required=False)
    municipality = forms.CharField(max_length=255, required=False)
    barangay = forms.CharField(max_length=255, required=False)
    specific_location = forms.CharField(max_length=255, required=False)

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')

        if selected_date is None:
            raise forms.ValidationError('Date and Time are required')
        if timezone.is_aware(selected_date):
            selected_date = timezone.localtime(selected_date)
        now = timezone.now()
        if selected_date.date() < (now + timedelta(days=3)).date():
            raise forms.ValidationError("Events must be scheduled at least 3 days in advance.")
        if selected_date.date() > (now + timedelta(days=5)).date():
            raise forms.ValidationError("Events can't be scheduled more than 5 days in advance.")

        return selected_date

    def clean(self):
        cleaned_data = super().clean()
        location_type = cleaned_data.get('location_type')

        if location_type == 'inside':
            if not cleaned_data.get('department') or not cleaned_data.get('building') or not cleaned_data.get('room_number'):
                raise forms.ValidationError("Department, Building, and Room Number are required for inside events.")

        elif location_type == 'outside':
            if not cleaned_data.get('province') or not cleaned_data.get('municipality') or not cleaned_data.get('barangay') or not cleaned_data.get('specific_location'):
                raise forms.ValidationError("Province, Municipality, Barangay, and Specific Location are required for outside events.")
        
        return cleaned_data


from django import forms
from .models import EventReminder

class EventReminderForm(forms.ModelForm):
    email = forms.EmailField(required=False)  

    class Meta:
        model = EventReminder
        fields = ['email']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feature', 'feedback_text', 'screenshot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class GroupRuleForm(forms.ModelForm):
    class Meta:
        model = GroupRule
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rule title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Rule description'}),
        }