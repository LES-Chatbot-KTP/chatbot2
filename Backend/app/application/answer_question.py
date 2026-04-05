"""Caso de uso: responder pergunta do usuário usando o banco de documentos."""
import re
from typing import List

import google.generativeai as genai
from django.conf import settings

from Backend.app.documents.models import Conversa, Mensagem, Documento
from Backend.app.domain.repositories.chunk_repository import ChunkRepository

_PROMPT_TEMPLATE = (
    "Você é um assistente especializado em documentos institucionais. "
    "Responda à pergunta usando exclusivamente o contexto abaixo. "
    "Se a resposta não estiver no contexto, informe que não há informação suficiente.\n\n"
    "Contexto:\n{contexto}\n\n"
    "Pergunta: {pergunta}\n\n"
    "Resposta:"
)


def preprocessar_pergunta(texto: str) -> str:
    """
    Pré-processa a pergunta do usuário:
    - Remove espaços extras
    - Converte para minúsculas
    - Remove caracteres especiais desnecessários
    """
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.lower()
    texto = re.sub(r'[^\w\s\?\!\.\,\á\é\í\ó\ú\ã\õ\â\ê\ô\ç]', '', texto)
    return texto


def _embed_query(texto: str) -> List[float]:
    """Gera embedding da query com task_type='retrieval_query'."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    result = genai.embed_content(
        model=settings.EMBEDDING_MODEL,
        content=texto,
        task_type="retrieval_query",
    )
    return result["embedding"]


class ResponderPergunta:
    """
    Caso de uso: pipeline RAG completo.

    Fluxo:
        1. Gera embedding da pergunta pré-processada (retrieval_query).
        2. Busca os top-K chunks mais relevantes via ChunkRepository (pgvector).
        3. Monta o contexto e gera resposta com o Gemini.
    """

    def __init__(self, chunk_repository: ChunkRepository) -> None:
        self._chunk_repo = chunk_repository

    def executar(self, pergunta_processada: str) -> dict:
        """
        Retorna dict com:
            - resposta:  str — texto gerado pelo Gemini
            - fontes:    list[dict] — documentos únicos usados, cada um com id e nome
        """
        query_embedding = _embed_query(pergunta_processada)
        chunks = self._chunk_repo.buscar_similares(query_embedding, settings.TOP_K)

        if not chunks:
            return {
                "resposta": "Não encontrei documentos indexados para responder à sua pergunta.",
                "fontes": [],
            }

        contexto = "\n\n---\n\n".join(
            f"[{chunk['documento_nome']}]\n{chunk['conteudo']}" for chunk in chunks
        )

        prompt = _PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta_processada)

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.CHAT_MODEL)
        resposta = model.generate_content(prompt).text

        # Deduplica documentos mantendo a ordem de relevância
        seen = set()
        fontes = []
        for chunk in chunks:
            doc_id = chunk["documento_id"]
            if doc_id not in seen:
                seen.add(doc_id)
                fontes.append({"id": doc_id, "nome": chunk["documento_nome"]})

        return {"resposta": resposta, "fontes": fontes}


def iniciar_conversa(user=None) -> Conversa:
    """Cria e retorna uma nova conversa. #34"""
    return Conversa.objects.create(user=user)


def registrar_mensagem(conversa: Conversa, pergunta_original: str) -> Mensagem:
    """
    Registra a pergunta original (#36) e a processada (#37).
    Retorna a mensagem criada.
    """
    pergunta_processada = preprocessar_pergunta(pergunta_original)

    mensagem = Mensagem.objects.create(
        conversa=conversa,
        role="user",
        conteudo_original=pergunta_original,       # #36 — pergunta como veio do usuário
        conteudo_processado=pergunta_processada,   # #37 — pergunta após processamento
    )
    return mensagem


def registrar_resposta(
    conversa: Conversa,
    resposta: str,
    ids_fontes: List[int] | None = None,
) -> Mensagem:
    """
    Registra a resposta do assistente e vincula os documentos de origem.

    Args:
        conversa:   sessão de chat.
        resposta:   texto gerado pelo modelo.
        ids_fontes: IDs dos Documentos usados como contexto RAG.
    """
    mensagem = Mensagem.objects.create(
        conversa=conversa,
        role="assistant",
        conteudo_original=resposta,
        conteudo_processado=resposta,
    )
    if ids_fontes:
        documentos = Documento.objects.filter(id__in=ids_fontes)
        mensagem.fontes.set(documentos)
    return mensagem