from django import forms
from .models import Recipe, Comment, Step
from django.forms.models import inlineformset_factory


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'category', 'image']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['instruction', 'image']


# Набор форм для шагов
StepFormSet = inlineformset_factory(
    Recipe,
    Step,
    form=StepForm,
    fields=['instruction', 'image'],
    extra=1,
    can_delete=True
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']