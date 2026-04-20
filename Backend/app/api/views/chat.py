from django.db.models import Count, Max

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from Backend.app.application.answer_question import (
    iniciar_conversa,
    registrar_mensagem,
    registrar_resposta,
)
from Backend.app.api.factories import ChatFactory
from Backend.app.documents.models import Conversa, Mensagem


class ChatIniciarView(APIView):
    """
    POST /api/chat/iniciar/
    Cria uma nova conversa e retorna o id da sessão. #34
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        conversa = iniciar_conversa(user=user)
        return Response(
            {
                "conversa_id": conversa.id,
                "iniciada_em": conversa.iniciada_em,
            },
            status=status.HTTP_201_CREATED,
        )


class ChatPerguntaView(APIView):
    """
    POST /api/chat/pergunta/
    Recebe uma pergunta, registra original e processada, retorna resposta.

    Body JSON:
        {
            "conversa_id":          1,
            "question":             "Qual o prazo?",
            "documento_id_filtro":  5     # opcional — após o usuário escolher
                                          # o contexto na tela de clarificação
        }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        conversa_id          = request.data.get("conversa_id")
        question             = request.data.get("question", "").strip()
        documento_id_filtro  = request.data.get("documento_id_filtro")

        if not question:
            return Response(
                {"error": "O campo 'question' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Normaliza o filtro (pode vir como string do front)
        if documento_id_filtro is not None:
            try:
                documento_id_filtro = int(documento_id_filtro)
            except (TypeError, ValueError):
                documento_id_filtro = None

        # Busca conversa existente ou cria uma nova
        if conversa_id:
            try:
                conversa = Conversa.objects.get(id=conversa_id)
            except Conversa.DoesNotExist:
                return Response(
                    {"error": "Conversa não encontrada."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            user = request.user if request.user.is_authenticated else None
            conversa = iniciar_conversa(user=user)

        # Registra pergunta original (#36) e processada (#37)
        mensagem = registrar_mensagem(conversa, question)

        # Gera e registra resposta via pipeline RAG
        responder = ChatFactory.make_responder()
        resultado = responder.executar(
            mensagem.conteudo_processado,
            documento_id_filtro=documento_id_filtro,
        )
        registrar_resposta(
            conversa,
            resultado["resposta"],
            ids_fontes=[f["id"] for f in resultado["fontes"]],
        )

        return Response(
            {
                "conversa_id":          conversa.id,
                "pergunta_original":    mensagem.conteudo_original,
                "pergunta_processada":  mensagem.conteudo_processado,
                "answer":               resultado["resposta"],
                "fontes":               resultado["fontes"],
                "citacoes":             resultado["citacoes"],
                "respondida":           resultado["respondida"],
                "intencao":             resultado["intencao"],
                "opcoes_clarificacao":  resultado.get("opcoes_clarificacao", []),
            },
            status=status.HTTP_200_OK,
        )


class ChatHistoricoView(APIView):
    """
    GET /api/chat/<conversa_id>/historico/
    Retorna o histórico completo de uma conversa.
    """

    def get(self, request, conversa_id: int):
        try:
            conversa = Conversa.objects.get(id=conversa_id)
        except Conversa.DoesNotExist:
            return Response(
                {"error": "Conversa não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mensagens = conversa.mensagens.prefetch_related("fontes").all()
        data = [
            {
                "id":                   m.id,
                "role":                 m.role,
                "conteudo_original":    m.conteudo_original,
                "conteudo_processado":  m.conteudo_processado,
                "criada_em":            m.criada_em,
                "fontes": [
                    {"id": d.id, "nome": d.nome}
                    for d in m.fontes.all()
                ],
            }
            for m in mensagens
        ]
        return Response({"conversa_id": conversa_id, "mensagens": data})


class ConversasUsuarioView(APIView):
    """
    GET /api/chat/conversas/
    Lista todas as conversas do usuário autenticado, da mais recente para a
    mais antiga. Usada para alimentar o histórico na sidebar.

    Resposta:
        {
            "conversas": [
                {
                    "id":                 12,
                    "iniciada_em":        "...",
                    "ultima_atualizacao": "...",
                    "total_mensagens":    8,
                    "titulo":             "Qual o prazo de matrícula?"
                },
                ...
            ]
        }
    """
    permission_classes = [IsAuthenticated]

    _TITULO_MAX_CHARS = 60

    def get(self, request):
        conversas = (
            Conversa.objects
            .filter(user=request.user)
            .annotate(
                ultima_atualizacao=Max("mensagens__criada_em"),
                total_mensagens=Count("mensagens"),
            )
            .order_by("-iniciada_em")
        )

        data = []
        for conv in conversas:
            primeira = (
                conv.mensagens
                .filter(role="user")
                .order_by("criada_em")
                .first()
            )
            if primeira:
                texto = primeira.conteudo_original.strip()
                titulo = texto[: self._TITULO_MAX_CHARS]
                if len(texto) > self._TITULO_MAX_CHARS:
                    titulo += "…"
            else:
                titulo = "Nova conversa"

            data.append({
                "id":                 conv.id,
                "iniciada_em":        conv.iniciada_em,
                "ultima_atualizacao": conv.ultima_atualizacao,
                "total_mensagens":    conv.total_mensagens,
                "titulo":             titulo,
            })

        return Response({"conversas": data})
