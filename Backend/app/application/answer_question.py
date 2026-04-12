"""Caso de uso: responder pergunta do usuário usando o banco de documentos."""
import re
import math
from django.conf import settings
from Backend.app.documents.models import Conversa, Mensagem, ChunkDocumento


def preprocessar_pergunta(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.lower()
    texto = re.sub(r'[^\w\s\?\!\.\,\á\é\í\ó\ú\ã\õ\â\ê\ô\ç]', '', texto)
    return texto


def iniciar_conversa(user=None) -> Conversa:
    """Cria e retorna uma nova conversa. #34"""
    return Conversa.objects.create(user=user)


def registrar_mensagem(conversa: Conversa, pergunta_original: str) -> Mensagem:
    """Registra a pergunta original (#36) e a processada (#37)."""
    pergunta_processada = preprocessar_pergunta(pergunta_original)
    mensagem = Mensagem.objects.create(
        conversa=conversa,
        role="user",
        conteudo_original=pergunta_original,
        conteudo_processado=pergunta_processada,
    )
    return mensagem


def _cosseno(a, b):
    """Similaridade de cosseno entre dois vetores."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embeddar(texto: str):
    """Gera embedding usando google.genai."""
    from google import genai
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={"api_version": "v1"},
    )
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=texto,
    )
    return result.embeddings[0].values


def _buscar_chunks(embedding_pergunta, top_k: int):
    """Busca os chunks mais relevantes por similaridade de cosseno."""
    chunks = ChunkDocumento.objects.exclude(embedding=None).select_related("documento")
    scored = []
    for chunk in chunks:
        if not chunk.embedding:
            continue
        sim = _cosseno(embedding_pergunta, chunk.embedding)
        scored.append((sim, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


# Frases que o modelo usa quando não encontra a informação nos documentos
_FRASES_SEM_RESPOSTA = [  # Lista de padrões textuais que indicam ausência de resposta
    "não encontrei a informação",
    "não encontrou a informação",
    "não há informações",
    "não tenho informações",
    "não está no contexto",
    "não foi encontrado",
    "não consta",
    "sem informações",
    "não possuo informações",
    "não disponho de informações",
]

# Mensagem padronizada exibida quando o modelo não encontra a informação nos documentos
_MENSAGEM_SEM_RESPOSTA = (
    "Não encontrei informações suficientes nos documentos disponíveis "
    "para responder a essa pergunta. Tente reformular ou consulte "
    "diretamente os documentos institucionais."
)

# Mensagem exibida quando não há nenhum documento indexado na base
_MENSAGEM_SEM_DOCUMENTOS = (
    "Ainda não há documentos indexados na base de conhecimento. "
    "Adicione documentos antes de fazer perguntas."
)

# Mensagem exibida quando ocorre falha na comunicação com a API do Gemini
_MENSAGEM_ERRO_API = (
    "Não foi possível processar sua pergunta no momento. "
    "Verifique sua conexão e tente novamente."
)


def _nao_soube_responder(texto: str) -> bool:  # Detecta se o modelo sinalizou que não encontrou a informação
    """Detecta se o modelo sinalizou que não encontrou a informação."""
    texto_lower = texto.lower()
    return any(frase in texto_lower for frase in _FRASES_SEM_RESPOSTA)


def gerar_resposta(pergunta_processada: str) -> tuple[str, bool]:  # Alterado: retorna tupla (resposta, respondida) em vez de só str
    """Busca contexto nos documentos e gera resposta via Gemini.

    Retorna (texto_resposta, respondida) onde `respondida` é False quando
    a pergunta não pôde ser respondida com os documentos disponíveis.
    """
    if not settings.GEMINI_API_KEY:
        return _MENSAGEM_ERRO_API, False  # Alterado: retorna tupla com flag False quando sem chave de API

    try:
        embedding_pergunta = _embeddar(pergunta_processada)
        top_k = getattr(settings, "TOP_K", 5)
        chunks_relevantes = _buscar_chunks(embedding_pergunta, top_k)

        if not chunks_relevantes:  # Alterado: trata ausência de documentos como caso separado
            return _MENSAGEM_SEM_DOCUMENTOS, False  # Alterado: retorna mensagem específica e flag False

        contexto = "\n\n".join(
            f"[{c.documento.nome}]\n{c.conteudo}" for c in chunks_relevantes
        )
        prompt = (
            "Você é um assistente especializado em documentos institucionais. "
            "Use apenas o contexto abaixo para responder em português. "
            "Se a resposta não estiver no contexto, responda EXATAMENTE: "  # Alterado: instrução explícita para o modelo usar frase detectável
            "'Não encontrei a informação nos documentos disponíveis.'\n\n"  # Alterado: frase-padrão que será detectada por _nao_soube_responder
            f"Contexto:\n{contexto}\n\n"
            f"Pergunta: {pergunta_processada}"
        )

        from google import genai
        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options={"api_version": "v1"},
        )
        response = client.models.generate_content(
            model=settings.CHAT_MODEL,
            contents=prompt,
        )
        texto = response.text  # Alterado: armazena o texto para verificar antes de retornar

        if _nao_soube_responder(texto):  # Alterado: verifica se o modelo indicou que não encontrou a informação
            return _MENSAGEM_SEM_RESPOSTA, False  # Alterado: substitui resposta vaga por mensagem padronizada com flag False

        return texto, True  # Alterado: retorna tupla com flag True quando a pergunta foi respondida com sucesso

    except Exception as e:
        return _MENSAGEM_ERRO_API, False  # Alterado: retorna mensagem amigável de erro com flag False em vez de expor a exceção


def registrar_resposta(conversa: Conversa, resposta: str) -> Mensagem:
    """Registra a resposta do assistente na conversa."""
    return Mensagem.objects.create(
        conversa=conversa,
        role="assistant",
        conteudo_original=resposta,
        conteudo_processado=resposta,
    )
