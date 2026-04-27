from django.db import migrations


IGNORAR = {
    "oi", "olá", "ola", "bom", "dia", "boa", "tarde", "noite",
    "obrigado", "obrigada", "valeu", "por", "favor",
}


def _gerar_titulo(pergunta: str, max_palavras: int = 8) -> str:
    import re

    texto = (pergunta or "").strip().lower()
    palavras = [
        palavra
        for palavra in re.findall(r"[\wáéíóúãõâêôç]+", texto, flags=re.IGNORECASE)
        if palavra not in IGNORAR
    ]
    if not palavras:
        return "Nova conversa"
    titulo = " ".join(palavras[:max_palavras]).strip()
    if len(palavras) > max_palavras:
        titulo += "..."
    return titulo[:1].upper() + titulo[1:]


def forwards(apps, schema_editor):
    Conversa = apps.get_model("documents", "Conversa")
    Mensagem = apps.get_model("documents", "Mensagem")

    for conversa in Conversa.objects.filter(titulo=""):
        primeira_pergunta = (
            Mensagem.objects.filter(conversa_id=conversa.id, role="user")
            .order_by("criada_em")
            .values_list("conteudo_original", flat=True)
            .first()
        )
        conversa.titulo = _gerar_titulo(primeira_pergunta or "")
        conversa.save(update_fields=["titulo"])


def backwards(apps, schema_editor):
    Conversa = apps.get_model("documents", "Conversa")
    Conversa.objects.all().update(titulo="")


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0007_conversa_titulo"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]