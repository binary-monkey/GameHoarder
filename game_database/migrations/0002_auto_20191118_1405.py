# Generated by Django 2.2.7 on 2019-11-18 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_database', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='developers',
            field=models.ManyToManyField(blank=True, related_name='game_developers', to='game_database.Company', verbose_name='developers'),
        ),
        migrations.AddField(
            model_name='game',
            name='publishers',
            field=models.ManyToManyField(blank=True, related_name='game_publishers', to='game_database.Company', verbose_name='publishers'),
        ),
        migrations.AddField(
            model_name='gameversion',
            name='name',
            field=models.CharField(blank=True, max_length=64, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='gameversion',
            name='developers',
            field=models.ManyToManyField(blank=True, related_name='version_developers', to='game_database.Company', verbose_name='developers'),
        ),
        migrations.AlterField(
            model_name='gameversion',
            name='publishers',
            field=models.ManyToManyField(blank=True, related_name='version_publishers', to='game_database.Company', verbose_name='publishers'),
        ),
    ]