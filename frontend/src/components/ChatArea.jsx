import { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown"; // <-- IMPORTAÇÃO DO MARKDOWN (Issue 2)
import "./ChatArea.css";
import enviarIcon from "../assets/images/enviar.svg";
import api from "../services/api.jsx";
import { authService } from "../services/authService";

export default function ChatArea() {
  const [mensagens, setMensagens] = useState([]);
  const [input, setInput] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [conversaId, setConversaId] = useState(null);
  const fimRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      setMensagens([]);
      setConversaId(null);
      return;
    }

    const conversaSelecionada = new URLSearchParams(location.search).get("conversa");

    if (conversaSelecionada) {
      setCarregando(true);
      api
        .get(`/api/chat/${conversaSelecionada}/historico/`)
        .then((res) => {
          const mensagensHistorico = (res.data.mensagens || []).map((m) => ({
            role: m.role,
            conteudo: m.conteudo_original,
            fontes: m.fontes ?? [],
            citacoes: [],
            respondida: true,
            avaliada: false,
          }));

          setConversaId(Number(conversaSelecionada));
          setMensagens(mensagensHistorico);
        })
        .catch((err) => {
          console.error("Erro ao carregar histórico da conversa:", err);
          setMensagens([]);
        })
        .finally(() => setCarregando(false));
      return;
    }

    setMensagens([]);
    setConversaId(null);
  }, [location.search]);

  useEffect(() => {
    fimRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensagens, carregando]);

  async function enviar() {
    const texto = input.trim();
    
    // ISSUE 1: VALIDAÇÃO DE ENTRADA DO USUÁRIO
    if (texto.length < 2) {
      alert("Por favor, digite uma pergunta válida com mais detalhes.");
      return;
    }
    if (carregando) return;

    setInput("");
    setMensagens((prev) => [...prev, { role: "user", conteudo: texto }]);
    setCarregando(true);

    try {
      const payload = { question: texto };
      if (conversaId) {
        payload.conversa_id = conversaId;
      }

      const res = await api.post("/api/chat/pergunta/", payload);

      if (!conversaId && res.data?.conversa_id) {
        setConversaId(res.data.conversa_id);
      }
      
      console.log("Resposta do servidor:", res.data); // <-- DEBUG: Pra gente ver o que chegou

      setMensagens((prev) => [
        ...prev,
        {
          role:       "assistant",
          id:         res.data.mensagem_id, // Issue 4 (ID para dar nota)
          conteudo:   res.data.answer,
          fontes:     res.data.fontes    ?? [],
          citacoes:   res.data.citacoes  ?? [],
          respondida: res.data.respondida,
          avaliada:   false, 
        },
      ]);
    } catch (error) {
      console.error("Erro na requisição da pergunta:", error);
      setMensagens((prev) => [
        ...prev,
        {
          role:       "assistant",
          conteudo:   "Não foi possível conectar ao servidor. Tente novamente.",
          fontes:     [],
          citacoes:   [],
          respondida: false,
        },
      ]);
    } finally {
      setCarregando(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      enviar();
    }
  }

  // ISSUE 4: FUNÇÃO PARA ENVIAR FEEDBACK DA RESPOSTA
  async function enviarFeedback(index, mensagemId, nota) {
    if (!mensagemId) return;
    try {
      await api.patch(`/api/chat/mensagem/${mensagemId}/feedback/`, { nota });
      setMensagens(prev => {
        const novas = [...prev];
        novas[index].avaliada = true;
        return novas;
      });
    } catch (err) {
      console.error("Erro ao enviar feedback", err);
      alert("Erro ao salvar feedback.");
    }
  }

  return (
    <div className="chatArea">
      <div className="mensagens">
        {mensagens.length === 0 ? (
          <div className="placeholder">
            <h2>Como posso ajudar?</h2>
          </div>
        ) : (
          <div className="listaMensagens">
            {mensagens.map((msg, i) => {
              const semResposta = msg.role === "assistant" && msg.respondida === false;
              return (
                <div key={i} className={`bolha ${msg.role}${semResposta ? " sem-resposta" : ""}`}>
                  {semResposta && (
                    <div className="sem-resposta-header">
                      <span className="sem-resposta-icone">&#9888;</span>
                      <span className="sem-resposta-titulo">Não foi possível responder</span>
                    </div>
                  )}

                  {/* ISSUE 2: MELHORIA DA FORMATAÇÃO (MARKDOWN) */}
                  <div className="textoBolha">
                    {msg.role === "assistant" ? (
                      <ReactMarkdown>{msg.conteudo || ""}</ReactMarkdown>
                    ) : (
                      msg.conteudo
                    )}
                  </div>

                  {msg.citacoes && msg.citacoes.length > 0 && (
                    <CitacoesArea citacoes={msg.citacoes} />
                  )}

                  {/* ISSUE 4: BOTÕES DE AVALIAÇÃO */}
                  {msg.role === "assistant" && msg.id && !semResposta && !msg.avaliada && (
                    <div className="feedbackArea">
                      <span className="feedbackPergunta">A resposta foi útil?</span>
                      <button onClick={() => enviarFeedback(i, msg.id, 1)} title="Sim">👍</button>
                      <button onClick={() => enviarFeedback(i, msg.id, -1)} title="Não">👎</button>
                    </div>
                  )}
                  {msg.avaliada && (
                     <div className="feedbackArea"><span className="feedbackObrigado">Obrigado pelo feedback! ✓</span></div>
                  )}
                </div>
              );
            })}

            {carregando && (
              <div className="bolha assistant">
                <div className="digitando">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
            <div ref={fimRef} />
          </div>
        )}
      </div>

      <div className="partedebaixo">
        <div className="mensagemArea">
          <input
            type="text"
            placeholder="Envie uma mensagem..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={carregando}
          />
          <button className="botaoEnviar" onClick={enviar} disabled={carregando || input.trim().length < 2}>
            <img src={enviarIcon} alt="Enviar" />
          </button>
        </div>
      </div>
    </div>
  );
}

function CitacoesArea({ citacoes }) {
  const [aberto, setAberto] = useState(false);
  return (
    <div className="citacoesArea">
      <button className="citacoesToggle" onClick={() => setAberto((v) => !v)} aria-expanded={aberto}>
        <span className="citacoesIcone">&#128196;</span>
        <span>{citacoes.length} fonte{citacoes.length !== 1 ? "s" : ""} consultada{citacoes.length !== 1 ? "s" : ""}</span>
        <span className="citacoesChevron">{aberto ? "▲" : "▼"}</span>
      </button>
      {aberto && (
        <ul className="citacoesList">
          {citacoes.map((c) => (
            <li key={c.ordem} className="citacaoCard">
              <div className="citacaoHeader">
                <span className="citacaoOrdem">{c.ordem}</span>
                <span className="citacaoDoc">{c.documento_nome}</span>
                {c.numero_pagina && <span className="citacaoPagina">pág.&nbsp;{c.numero_pagina}</span>}
              </div>
              <blockquote className="citacaoTrecho">"{c.trecho}"</blockquote>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}