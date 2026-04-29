from django.db import models
from django.contrib.auth.models import User


class AgentCommercial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Category(models.Model):
    """Catégorie d'assurance: Véhicule tourisme, 2 Roues, etc."""
    code_categorie = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code Catégorie",
        help_text="Code convenu entre l'agence et Atlanta Sanad (ex: VT, 2R, TC...)"
    )
    category_name = models.CharField(max_length=100, verbose_name="Libellé Catégorie")
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.code_categorie} — {self.category_name}"

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['code_categorie']


class Vehicle(models.Model):
    marque = models.CharField(max_length=100, verbose_name="Marque")
    immatriculation = models.CharField(max_length=50, verbose_name="Immatriculation", unique=True)
    categorie = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Catégorie")

    def __str__(self):
        return f"{self.marque} - {self.immatriculation}"


class Dossier(models.Model):
    """Core model — maps directly to the production sheet."""

    PAYMENT_CHOICES = [
        ('Espèce', 'Espèce'),
        ('Chèque', 'Chèque'),
        ('Virement', 'Virement'),
        ('TPE', 'TPE'),
    ]

    STATUS_CHOICES = [
        ('Actif', 'Actif'),
        ('Expiré', 'Expiré'),
        ('Annulé', 'Annulé'),
        ('En attente', 'En attente'),
    ]

    # --- Identification ---
    numero_dossier = models.PositiveIntegerField(verbose_name="N° Dossier", unique=True)
    assure = models.CharField(max_length=200, verbose_name="Assuré(e)")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True)

    # --- Police & Attestation ---
    numero_police = models.CharField(max_length=100, verbose_name="Police N°")
    numero_attestation = models.CharField(max_length=100, verbose_name="Attestation N°", blank=True)
    numero_quittance = models.CharField(max_length=100, verbose_name="Quittance N°", blank=True)

    # --- Vehicle ---
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Véhicule")

    # --- Dates ---
    date_effet = models.DateField(verbose_name="Date d'effet")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    date_creation = models.DateField(auto_now_add=True)

    # --- Financial ---
    prime_totale = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prime Totale (MAD)")
    montant_encaisse = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant Encaissé (MAD)")
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Espèce', verbose_name="Mode de Paiement")
    date_reglement = models.DateField(null=True, blank=True, verbose_name="Date de Règlement")

    # --- Status & Notes ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Actif', verbose_name="Statut")
    observation = models.TextField(blank=True, verbose_name="Observation")

    # --- Agent ---
    agent_commercial = models.ForeignKey(
        AgentCommercial, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Agent Commercial"
    )

    @property
    def reste(self):
        return self.prime_totale - self.montant_encaisse

    @property
    def est_solde(self):
        return self.reste <= 0

    def __str__(self):
        return f"Dossier {self.numero_dossier} - {self.assure}"

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"


class RemiseCompagnie(models.Model):
    STATUS_CHOICES = [
        ('En attente', 'En attente'),
        ('Remis', 'Remis'),
        ('Confirmé', 'Confirmé'),
    ]

    dossiers = models.ManyToManyField(Dossier, verbose_name="Dossiers inclus")
    date_remise = models.DateField(verbose_name="Date de Remise")
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant Total Remis (MAD)")
    commission_agence = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Commission Agence (MAD)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En attente')
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence Remise")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Remise {self.reference} - {self.date_remise}"

    class Meta:
        ordering = ['-date_remise']
        verbose_name = "Remise Compagnie"
        verbose_name_plural = "Remises Compagnie"


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=500)
    admin_comment = models.CharField(max_length=200, default='Sans réponse')
    asked_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.description
