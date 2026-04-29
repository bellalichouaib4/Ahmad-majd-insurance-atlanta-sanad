from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0002_category_code_categorie'),
    ]

    operations = [
        # --- Create Client table ---
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_complet', models.CharField(max_length=200, verbose_name='Nom Complet')),
                ('telephone', models.CharField(blank=True, max_length=20, verbose_name='T\u00e9l\u00e9phone')),
                ('cin', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='CIN')),
                ('adresse', models.CharField(blank=True, max_length=300, verbose_name='Adresse')),
                ('email', models.EmailField(blank=True, verbose_name='Email')),
                ('date_creation', models.DateField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Client', 'verbose_name_plural': 'Clients', 'ordering': ['nom_complet']},
        ),
        # --- Add new fields to Vehicle ---
        migrations.AddField(
            model_name='vehicle',
            name='modele',
            field=models.CharField(blank=True, max_length=100, verbose_name='Mod\u00e8le'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='annee',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Ann\u00e9e'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='type_vehicule',
            field=models.CharField(
                choices=[('Tourisme','Tourisme'),('2 Roues','2 Roues'),('Transport en Commun','Transport en Commun'),('Utilitaire','Utilitaire'),('Camion','Camion'),('Autre','Autre')],
                default='Tourisme', max_length=30, verbose_name='Type de V\u00e9hicule'
            ),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='client',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='vehicles',
                to='insurance.client',
                verbose_name='Client Propri\u00e9taire'
            ),
        ),
        # --- Add client FK to Dossier ---
        migrations.AddField(
            model_name='dossier',
            name='client',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='dossiers',
                to='insurance.client',
                verbose_name='Client Assur\u00e9'
            ),
        ),
    ]
