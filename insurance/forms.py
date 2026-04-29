from django import forms
from django.contrib.auth.models import User
from . import models


class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ['code_categorie', 'category_name']
        labels = {
            'code_categorie': 'Code Catégorie',
            'category_name': 'Libellé / Nom de la Catégorie',
        }
        help_texts = {
            'code_categorie': "Code convenu entre l'agence et Atlanta Sanad (ex : VT, 2R, TC, MRC...)",
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = models.Vehicle
        fields = ['marque', 'immatriculation', 'categorie']
        labels = {
            'marque': 'Marque',
            'immatriculation': 'Immatriculation',
            'categorie': 'Catégorie',
        }


class DossierForm(forms.ModelForm):
    class Meta:
        model = models.Dossier
        fields = [
            'numero_dossier', 'assure', 'telephone',
            'numero_police', 'numero_attestation', 'numero_quittance',
            'vehicle',
            'date_effet', 'date_echeance',
            'prime_totale', 'montant_encaisse', 'mode_paiement', 'date_reglement',
            'status', 'observation', 'agent_commercial'
        ]
        widgets = {
            'date_effet': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'date_reglement': forms.DateInput(attrs={'type': 'date'}),
            'observation': forms.Textarea(attrs={'rows': 3}),
        }


class RemiseCompagnieForm(forms.ModelForm):
    dossiers = forms.ModelMultipleChoiceField(
        queryset=models.Dossier.objects.all().order_by('-date_creation'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Dossiers Inclus"
    )

    class Meta:
        model = models.RemiseCompagnie
        fields = ['reference', 'date_remise', 'dossiers', 'montant_total', 'commission_agence', 'status', 'notes']
        widgets = {
            'date_remise': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'reference': 'Référence Remise',
            'date_remise': 'Date de Remise',
            'montant_total': 'Montant Total Remis (MAD)',
            'commission_agence': 'Commission Agence (MAD)',
            'status': 'Statut',
            'notes': 'Notes',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})
        }
