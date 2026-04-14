from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_conversa_mensagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensagem',
            name='fontes',
            field=models.ManyToManyField(
                blank=True,
                related_name='mensagens_origem',
                to='documents.documento',
            ),
        ),
    ]
