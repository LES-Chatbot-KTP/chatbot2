import { useState, useRef, useEffect } from "react";
import "./ChatArea.css";
import enviarIcon from "../assets/images/enviar.svg";
import api from "../services/api";

export default function ChatArea() {
  const [mensagens, setMensagens] = useState([]);
  const [input, setInput] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [conversaId, setConversaId] = useState(null);
  const mensagensRef = useRef(null);

  // Rola para o final sempre que novas mensagens chegam
  useEffect(() => {
    if (mensagensRef.current) {
      mensagensRef.current.scrollTop = mensagensRef.current.scrollHeight;
    }
  }, [mensagens, carregando]);

  async function enviarMensagem() {
    const texto = input.trim();
    if (!texto || carregando) return;

    // Exibe a mensagem do usuário imediatamente
    const novaMensagemUsuario = { role: "user", conteudo: texto };
    setMensagens((prev) => [...prev, novaMensagemUsuario]);
    setInput("");
    setCarregando(true);

    try {
      // Conecta ao endpoint da API
      const response = await api.post("/api/chat/pergunta/", {
        conversa_id: conversaId,
        question: texto,
      });

      const { answer, conversa_id, pergunta_processada } = response.data;

      // Salva o conversa_id para manter o contexto da conversa
      if (!conversaId) setConversaId(conversa_id);

      // Exibe resposta textual
      // Exibe origem da informação
      const novaMensagemBot = {
        role: "bot",
        conteudo: answer,
        conversa_id: conversa_id,
        pergunta_processada: pergunta_processada,
      };
      setMensagens((prev) => [...prev, novaMensagemBot]);
    } catch (error) {
      const errMsg =
        error?.response?.data?.error || "Erro ao conectar com o servidor.";
      setMensagens((prev) => [
        ...prev,
        { role: "bot", conteudo: errMsg, erro: true },
      ]);
    } finally {
      setCarregando(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      enviarMensagem();
    }
  }

  const semMensagens = mensagens.length === 0;

  return (
    <div className="chatArea">
      {/* Área de mensagens */}
      <div className="mensagens" ref={mensagensRef}>
        {semMensagens ? (
          <div className="placeholder">
            <h2>Como posso ajudar?</h2>
          </div>
        ) : (
          <div className="listaMensagens">
            {mensagens.map((msg, i) => (
              <div
                key={i}
                className={`bolha bolha-${msg.role} ${msg.erro ? "bolha-erro" : ""}`}
              >
                <p className="bolha-texto">{msg.conteudo}</p>

                {/* Exibe origem da informação apenas nas respostas do bot */}
                {msg.role === "bot" && !msg.erro && msg.conversa_id && (
                  <span className="bolha-origem">
                    Conversa #{msg.conversa_id}
                    {msg.pergunta_processada &&
                    msg.pergunta_processada !== msg.conteudo
                      ? ` · Processado: "${msg.pergunta_processada}"`
                      : ""}
                  </span>
                )}
              </div>
            ))}

            {/* Indicador de carregamento */}
            {carregando && (
              <div className="bolha bolha-bot bolha-carregando">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input */}
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
          <button
            className="botaoEnviar"
            onClick={enviarMensagem}
            disabled={carregando || !input.trim()}
          >
            <img src={enviarIcon} alt="Enviar" />
          </button>
        </div>
      </div>
    </div>
  );
}
