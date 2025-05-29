from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FinancialGoal


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# forms.py

from .models import BudgetEntry

class BudgetEntryForm(forms.ModelForm):
    class Meta:
        model = BudgetEntry
        fields = ['month', 'budget', 'expenses']
