"""
PostgreSQL implementation of ChunkRepository using pgvector.

O campo `embedding` é armazenado como JSONField (JSONB no PostgreSQL).
O cast `embedding::text::vector` converte o array JSON para o tipo nativo
do pgvector, permitindo usar o operador `<=>` (distância de cosseno).
"""

import json
from typing import List

from django.db import connection

from Backend.app.domain.repositories.chunk_repository import ChunkRepository

_SQL = """
    SELECT
        c.id,
        c.conteudo,
        d.id   AS documento_id,
        d.nome AS documento_nome
    FROM documents_chunkdocumento c
    INNER JOIN documents_documento d ON d.id = c.documento_id
    WHERE c.embedding IS NOT NULL
    ORDER BY c.embedding::text::vector <=> %s::vector
    LIMIT %s
"""


class PostgresChunkRepository(ChunkRepository):

    def buscar_similares(self, query_embedding: List[float], top_k: int) -> List[dict]:
        """
        Executa busca vetorial por cosseno diretamente no PostgreSQL via pgvector.

        Args:
            query_embedding: vetor da pergunta (gerado com task_type='retrieval_query').
            top_k:           número máximo de chunks a retornar.

        Returns:
            Lista de dicts com chaves: id, conteudo, documento_nome.
        """
        with connection.cursor() as cursor:
            cursor.execute(_SQL, [json.dumps(query_embedding), top_k])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
