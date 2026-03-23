"""
View para operações sobre documentos.
Usa DocumentFactory (Factory Method) para obter o caso de uso.
Requer autenticação JWT — apenas administradores podem excluir documentos.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from Backend.app.api.factories import DocumentFactory


class DocumentListView(APIView):
    """
    GET /api/documents/
    Lista os arquivos enviados à API do Gemini via genai.list_files().
    Requer token JWT de administrador no header:
        Authorization: Bearer <access_token>
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        caso_de_uso = DocumentFactory.make_list()

        try:
            resultado = caso_de_uso.executar()
            return Response({"documentos": resultado}, status=status.HTTP_200_OK)

        except RuntimeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """
        POST /api/documents/
        Cadastra um novo documento: faz upload para o Gemini e salva no banco.

        Body (multipart/form-data):
            nome    — nome do documento (obrigatório)
            tipo    — portaria | resolucao | rod (obrigatório)
            arquivo — arquivo a ser enviado (obrigatório)
        """
        nome = request.data.get("nome", "").strip()
        tipo = request.data.get("tipo", "").strip()
        arquivo = request.FILES.get("arquivo")

        if not arquivo:
            return Response(
                {"error": "O campo 'arquivo' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        caso_de_uso = DocumentFactory.make_create()

        try:
            resultado = caso_de_uso.executar(
                nome=nome,
                tipo=tipo,
                conteudo_arquivo=arquivo.read(),
                nome_arquivo=arquivo.name,
            )
            return Response(resultado, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except RuntimeError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDeleteView(APIView):
    """
    DELETE /api/documents/<id>/
    Exclui um documento e todos os seus chunks do banco de dados.
    Requer token JWT de administrador no header:
        Authorization: Bearer <access_token>
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, id_documento: int):
        caso_de_uso = DocumentFactory.make_delete()

        try:
            resultado = caso_de_uso.executar(id_documento)
            return Response(resultado, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except LookupError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )