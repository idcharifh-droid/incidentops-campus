from django import forms
from .models import Ticket, Comment, Attachment
from categories.models import Category


class TicketCreateForm(forms.ModelForm):
    attachment = forms.FileField(required=False, label='Pièce jointe')

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        labels = {
            'title': 'Titre de l\'incident',
            'description': 'Description détaillée',
            'category': 'Catégorie',
            'priority': 'Priorité',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].empty_label = '-- Laisser l\'IA choisir --'
        self.fields['category'].required = False
        self.fields['priority'].required = False


class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'is_internal']
        labels = {
            'content': 'Commentaire',
            'is_internal': 'Note interne (visible uniquement par les techniciens)',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Votre commentaire...'}),
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
        labels = {'file': 'Fichier'}
