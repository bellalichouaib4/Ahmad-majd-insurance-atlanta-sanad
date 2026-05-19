from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0005_seed_categories_dossier_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='dossier',
            name='categorie',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='dossiers',
                to='insurance.Category',
                verbose_name='Catégorie',
            ),
        ),
    ]
