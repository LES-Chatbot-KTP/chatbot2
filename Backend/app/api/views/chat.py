from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ChatView(APIView):
    def post(self, request):
        question = request.data.get("question", "")

        if not question:
            return Response(
                {"error": "O campo 'question' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"answer": f"Você perguntou: {question}"},
            status=status.HTTP_200_OK,
        )