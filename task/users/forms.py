from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile, LateFeeConfig

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username',  'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}), 
            'password': forms.PasswordInput(attrs={'class': 'form-control'}), 
        }

class GoogleLoginProfileForm(forms.ModelForm):
    """Form for profiles created through Google login."""
    
    class Meta:
        model = Profile
        fields = ['name', 'room', 'hostel']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].required = True  # Ensure room is required for students
        self.fields['hostel'].required = True  # Ensure hostel is required for students

    def save(self, commit=True):
        """Automatically set role as student for Google login."""
        profile = super().save(commit=False)
        profile.role = 'student'
        if commit:
            profile.save()
        return profile


class ManualRegistrationProfileForm(forms.ModelForm):
    """Form for profiles created through username-password login."""
    email = forms.EmailField(required=True)  # Email stored in User, not Profile
    
    class Meta:
        model = Profile
        fields = ['name', 'psrn_number']  # Email is excluded as it is stored in User model
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('role') == 'student':  # If role is 'student', disable the PSRN field
            self.fields['psrn_number'].disabled = True

    def save(self, commit=True):
        """Save Profile data and update the email of the logged-in user."""
        profile = super().save(commit=False)
        
        if commit:
            profile.save()  # Save the Profile object
        
        return profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'psrn_number', 'room', 'hostel']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            if user.profile.role == 'student':  
                self.fields.pop('psrn_number', None)
            elif user.profile.role == 'librarian':
                self.fields.pop('room', None)  # Remove PSRN field for librarians
                self.fields.pop('hostel', None)


class LateFeeConfigForm(forms.ModelForm):
    class Meta:
        model = LateFeeConfig
        fields = ['days_before_late_fee', 'late_fee_per_day']
        widgets = {
            'late_fee_per_day': forms.NumberInput(attrs={'min': '1.00', 'step': '0.01'}),
            'days_before_late_fee': forms.NumberInput(attrs={'min': '1'}),
        }



