from django.db import models
from django.contrib.auth.models import User


class AgentCommercial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Category(models.Model):
    code_categorie = models.CharField(
        max_length=50, unique=True,
        verbose_name="Code Cat\u00e9gorie",
        help_text="Code convenu entre l'agence et Atlanta Sanad (ex: VT, 2R, TC...)"
    )
    category_name = models.CharField(max_length=100, verbose_name="Libell\u00e9")
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.code_categorie} \u2014 {self.category_name}"

    class Meta:
        verbose_name = "Cat\u00e9gorie"
        verbose_name_plural = "Cat\u00e9gories"
        ordering = ['code_categorie']


class Client(models.Model):
    """Standalone client record — reused across multiple dossiers."""
    nom_complet = models.CharField(max_length=200, verbose_name="Nom Complet")
    telephone = models.CharField(max_length=20, verbose_name="T\u00e9l\u00e9phone", blank=True)
    cin = models.CharField(max_length=30, verbose_name="CIN", blank=True, unique=True, null=True)
    adresse = models.CharField(max_length=300, verbose_name="Adresse", blank=True)
    email = models.EmailField(blank=True, verbose_name="Email")
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        parts = [self.nom_complet]
        if self.telephone:
            parts.append(self.telephone)
        if self.cin:
            parts.append(self.cin)
        return " \u2014 ".join(parts)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom_complet']


class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('Tourisme', 'Tourisme'),
        ('2 Roues', '2 Roues'),
        ('Transport en Commun', 'Transport en Commun'),
        ('Utilitaire', 'Utilitaire'),
        ('Camion', 'Camion'),
        ('Autre', 'Autre'),
    ]
    # link vehicle to a client (optional for now)
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Client Propri\u00e9taire",
        related_name='vehicles'
    )
    marque = models.CharField(max_length=100, verbose_name="Marque")
    modele = models.CharField(max_length=100, verbose_name="Mod\u00e8le", blank=True)
    immatriculation = models.CharField(max_length=50, verbose_name="Immatriculation", unique=True)
    annee = models.PositiveIntegerField(verbose_name="Ann\u00e9e", null=True, blank=True)
    type_vehicule = models.CharField(
        max_length=30, choices=TYPE_CHOICES,
        default='Tourisme', verbose_name="Type de V\u00e9hicule"
    )
    categorie = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Cat\u00e9gorie d'Assurance"
    )

    def __str__(self):
        return f"{self.marque} {self.modele} \u2014 {self.immatriculation}"

    class Meta:
        verbose_name = "V\u00e9hicule"
        verbose_name_plural = "V\u00e9hicules"


class Dossier(models.Model):
    PAYMENT_CHOICES = [
        ('Esp\u00e8ce', 'Esp\u00e8ce'),
        ('Ch\u00e8que', 'Ch\u00e8que'),
        ('Virement', 'Virement'),
        ('TPE', 'TPE'),
    ]
    STATUS_CHOICES = [
        ('Actif', 'Actif'),
        ('Expir\u00e9', 'Expir\u00e9'),
        ('Annul\u00e9', 'Annul\u00e9'),
        ('En attente', 'En attente'),
    ]

    numero_dossier = models.PositiveIntegerField(verbose_name="N\u00b0 Dossier", unique=True)

    # --- Client (replaces raw assure/telephone fields) ---
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Client Assur\u00e9",
        related_name='dossiers'
    )
    # kept for legacy/manual entry fallback
    assure = models.CharField(max_length=200, verbose_name="Assur\u00e9(e)", blank=True)
    telephone = models.CharField(max_length=20, verbose_name="T\u00e9l\u00e9phone", blank=True)

    # --- Police & Documents ---
    numero_police = models.CharField(max_length=100, verbose_name="Police N\u00b0")
    numero_attestation = models.CharField(max_length=100, verbose_name="Attestation N\u00b0", blank=True)
    numero_quittance = models.CharField(max_length=100, verbose_name="Quittance N\u00b0", blank=True)

    # --- Vehicle ---
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="V\u00e9hicule"
    )

    # --- Dates ---
    date_effet = models.DateField(verbose_name="Date d'effet")
    date_echeance = models.DateField(verbose_name="Date d'\u00e9ch\u00e9ance")
    date_creation = models.DateField(auto_now_add=True)

    # --- Financial ---
    prime_totale = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prime Totale (MAD)")
    montant_encaisse = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant Encaiss\u00e9 (MAD)")
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Esp\u00e8ce', verbose_name="Mode de Paiement")
    date_reglement = models.DateField(null=True, blank=True, verbose_name="Date de R\u00e8glement")

    # --- Status & Notes ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Actif', verbose_name="Statut")
    observation = models.TextField(blank=True, verbose_name="Observation")

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

    def get_assure_display(self):
        if self.client:
            return self.client.nom_complet
        return self.assure

    def get_telephone_display(self):
        if self.client:
            return self.client.telephone
        return self.telephone

    def __str__(self):
        return f"Dossier {self.numero_dossier} - {self.get_assure_display()}"

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"


class RemiseCompagnie(models.Model):
    STATUS_CHOICES = [
        ('En attente', 'En attente'),
        ('Remis', 'Remis'),
        ('Confirm\u00e9', 'Confirm\u00e9'),
    ]
    dossiers = models.ManyToManyField(Dossier, verbose_name="Dossiers inclus")
    date_remise = models.DateField(verbose_name="Date de Remise")
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant Total Remis (MAD)")
    commission_agence = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Commission Agence (MAD)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En attente')
    reference = models.CharField(max_length=100, blank=True, verbose_name="R\u00e9f\u00e9rence Remise")
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
    admin_comment = models.CharField(max_length=200, default='Sans r\u00e9ponse')
    asked_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.description
