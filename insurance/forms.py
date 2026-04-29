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
            'code_categorie': 'Code Cat\u00e9gorie',
            'category_name': 'Libell\u00e9 / Nom',
        }
        help_texts = {
            'code_categorie': "Code officiel Atlanta Sanad (ex\u00a0: VT, 2R, TC, MRC...)",
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ['nom_complet', 'telephone', 'cin', 'adresse', 'email']
        labels = {
            'nom_complet': 'Nom Complet',
            'telephone': 'T\u00e9l\u00e9phone',
            'cin': 'CIN / N\u00b0 Identit\u00e9',
            'adresse': 'Adresse',
            'email': 'Email',
        }
        widgets = {
            'adresse': forms.TextInput(attrs={'placeholder': 'Adresse compl\u00e8te...'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = models.Vehicle
        fields = ['client', 'marque', 'modele', 'immatriculation', 'annee', 'type_vehicule', 'categorie']
        labels = {
            'client': 'Client Propri\u00e9taire',
            'marque': 'Marque',
            'modele': 'Mod\u00e8le',
            'immatriculation': 'Immatriculation',
            'annee': 'Ann\u00e9e',
            'type_vehicule': 'Type de V\u00e9hicule',
            'categorie': "Cat\u00e9gorie d'Assurance",
        }


class DossierForm(forms.ModelForm):
    class Meta:
        model = models.Dossier
        fields = [
            'numero_dossier',
            'client',
            'assure', 'telephone',
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
        labels = {
            'numero_dossier': 'N\u00b0 Dossier',
            'client': 'Client (depuis la liste)',
            'assure': 'Assur\u00e9(e) (manuel)',
            'telephone': 'T\u00e9l\u00e9phone (manuel)',
            'numero_police': 'Police N\u00b0',
            'numero_attestation': 'Attestation N\u00b0',
            'numero_quittance': 'Quittance N\u00b0',
            'vehicle': 'V\u00e9hicule',
            'date_effet': "Date d'Effet",
            'date_echeance': "Date d'\u00c9ch\u00e9ance",
            'prime_totale': 'Prime Totale (MAD)',
            'montant_encaisse': 'Montant Encaiss\u00e9 (MAD)',
            'mode_paiement': 'Mode de Paiement',
            'date_reglement': 'Date de R\u00e8glement',
            'status': 'Statut',
            'observation': 'Observation',
            'agent_commercial': 'Agent Commercial',
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


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['description']
        widgets = {'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})}
