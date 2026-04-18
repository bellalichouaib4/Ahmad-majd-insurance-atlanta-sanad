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
        fields = ['category_name']
        labels = {'category_name': "Catégorie d'assurance"}


class VehicleForm(forms.ModelForm):
    class Meta:
        model = models.Vehicle
        fields = ['marque', 'immatriculation', 'categorie']
        labels = {
            'marque': 'Marque',
            'immatriculation': 'Immatriculation',
            'categorie': "Catégorie",
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
    class Meta:
        model = models.RemiseCompagnie
        fields = ['dossiers', 'date_remise', 'montant_total', 'commission_agence', 'status', 'reference', 'notes']
        widgets = {
            'date_remise': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'dossiers': forms.CheckboxSelectMultiple(),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})
        }
