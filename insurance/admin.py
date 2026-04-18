from django.contrib import admin
from .models import AgentCommercial, Category, Vehicle, Dossier, RemiseCompagnie, Question


@admin.register(AgentCommercial)
class AgentCommercialAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'mobile', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'creation_date']
    search_fields = ['category_name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['marque', 'immatriculation', 'categorie']
    search_fields = ['marque', 'immatriculation']
    list_filter = ['categorie']


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = [
        'numero_dossier', 'assure', 'numero_police',
        'date_effet', 'date_echeance',
        'prime_totale', 'montant_encaisse', 'reste',
        'mode_paiement', 'status', 'agent_commercial'
    ]
    search_fields = ['assure', 'numero_police', 'numero_attestation', 'numero_quittance']
    list_filter = ['status', 'mode_paiement', 'agent_commercial', 'vehicle__categorie']
    readonly_fields = ['reste', 'est_solde', 'date_creation']
    date_hierarchy = 'date_effet'
    ordering = ['-date_creation']

    fieldsets = (
        ('Identification', {
            'fields': ('numero_dossier', 'assure', 'telephone', 'status')
        }),
        ('Police & Documents', {
            'fields': ('numero_police', 'numero_attestation', 'numero_quittance')
        }),
        ('Véhicule', {
            'fields': ('vehicle',)
        }),
        ('Dates', {
            'fields': ('date_effet', 'date_echeance')
        }),
        ('Financier', {
            'fields': ('prime_totale', 'montant_encaisse', 'reste', 'est_solde', 'mode_paiement', 'date_reglement')
        }),
        ('Agent & Notes', {
            'fields': ('agent_commercial', 'observation')
        }),
    )


@admin.register(RemiseCompagnie)
class RemiseCompagnieAdmin(admin.ModelAdmin):
    list_display = ['reference', 'date_remise', 'montant_total', 'commission_agence', 'status']
    list_filter = ['status']
    search_fields = ['reference']
    filter_horizontal = ['dossiers']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'asked_date', 'admin_comment']
