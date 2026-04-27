import "./ConhecimentoArea.css";
import { useEffect, useMemo, useState } from "react";
import Documento from "./Documento";
import api from "../services/api.jsx";
import { authService } from "../services/authService";

import recarregar from "../assets/images/reload.svg";

export default function ConhecimentoArea() {
  const [modalOpen, setModalOpen] = useState(false);
  const [documentos, setDocumentos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      setLoading(false);
      setDocumentos([]);
      return;
    }

    api
      .get("/api/documents/")
      .then((res) => {
        setDocumentos(res.data?.documentos ?? []);
      })
      .catch((err) => {
        console.error("Erro ao buscar documentos:", err);
        setDocumentos([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const resumo = useMemo(() => {
    const total = documentos.length;
    const indexados = documentos.filter((d) => d.status === "indexado").length;
    const pendentes = total - indexados;
    const ultimaAtualizacao = documentos.length
      ? new Date(documentos[0].atualizado_em).toLocaleDateString("pt-BR")
      : "-";
    return { total, indexados, pendentes, ultimaAtualizacao };
  }, [documentos]);

  function formatarTipo(tipo) {
    if (tipo === "portaria") return "Portaria";
    if (tipo === "resolucao") return "Resolução";
    if (tipo === "rod") return "ROD";
    return tipo || "-";
  }

  function formatarData(dataIso) {
    if (!dataIso) return "-";
    const d = new Date(dataIso);
    return `${d.toLocaleDateString("pt-BR")} ${d.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    })}`;
  }

  return (
    <div className="conhecArea">
      <div className="topo">
        <h2>Base de Conhecimento</h2>
        <button className="btnAdd" onClick={() => setModalOpen(true)}>
          + Adicionar documento
        </button>
      </div>

      <div className="dadosDoc">
        <div className="cardDados">
          <h2>Total de Documentos</h2>
          <h2>{resumo.total}</h2>
        </div>
        <div className="cardDados">
          <h2>Última Atualização</h2>
          <h2>{resumo.ultimaAtualizacao}</h2>
        </div>
        <div className="cardDados">
          <h2>Indexados</h2>
          <h2>{resumo.indexados}</h2>
        </div>
        <div className="cardDados">
          <h2>Pendentes</h2>
          <h2>{resumo.pendentes}</h2>
        </div>
      </div>

      <div className="areaDocumentos">
        <div className="listaDocumentos">
          <div className="headerDoc">
            <h2>Documentos</h2>
            <button className="btnReindexar">
              <img src={recarregar} alt="Reindexar" />
              Reindexar todos
            </button>
          </div>

          <div className="listaScroll">
            {loading ? (
              <div className="documento" style={{ opacity: 0.8 }}>
                Carregando documentos reais...
              </div>
            ) : documentos.length === 0 ? (
              <div className="documento" style={{ opacity: 0.8 }}>
                Nenhum documento encontrado no banco.
              </div>
            ) : (
              documentos.map((doc) => (
                <Documento
                  key={doc.id}
                  titulo={doc.nome}
                  conteudo={`(${doc.total_chunks} chunks)`}
                  categoria={formatarTipo(doc.tipo)}
                  dataCriacao={formatarData(doc.indexado_em)}
                  ultimaAtualizacao={formatarData(doc.atualizado_em)}
                  status={doc.status}
                />
              ))
            )}
          </div>
        </div>
      </div>

      {/* MODAL */}
      {modalOpen && (
        <div className="overlay">
          <div className="modal">
            <h2>Novo Documento</h2>

            <label>
              Título
              <input type="text" placeholder="Digite o título" />
            </label>

            <label>
              Categoria
              <input type="text" placeholder="Digite a categoria" />
            </label>

            <label>
              Conteúdo
              <input type="text" placeholder="Digite o conteúdo..." />
            </label>

            <label>
              Origem
              <input type="text" placeholder="Digite a origem" />
            </label>

            <div className="modalActions">
              <button className="btnVoltar" onClick={() => setModalOpen(false)}>
                Voltar
              </button>

              <button className="btnSalvar">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
