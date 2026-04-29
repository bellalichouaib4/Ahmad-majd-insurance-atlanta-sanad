from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='code_categorie',
            field=models.CharField(
                default='',
                help_text="Code convenu entre l'agence et Atlanta Sanad (ex: VT, 2R, TC...)",
                max_length=50,
                unique=True,
                verbose_name='Code Cat\u00e9gorie',
            ),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['code_categorie'], 'verbose_name': 'Cat\u00e9gorie', 'verbose_name_plural': 'Cat\u00e9gories'},
        ),
        migrations.AlterField(
            model_name='category',
            name='category_name',
            field=models.CharField(max_length=100, verbose_name='Libell\u00e9 Cat\u00e9gorie'),
        ),
    ]
