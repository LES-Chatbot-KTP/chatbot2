import { useState, useEffect, useRef } from "react";
import "./ChatArea.css";
import enviarIcon from "../assets/images/enviar.svg";
import api from "../services/api.jsx";

export default function ChatArea() {
  const [mensagens, setMensagens] = useState([]);
  const [input, setInput] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [conversaId, setConversaId] = useState(null);
  const fimRef = useRef(null);

  useEffect(() => {
    api
      .post("/api/chat/iniciar/")
      .then((res) => setConversaId(res.data.conversa_id))
      .catch((err) => console.error("Erro ao iniciar conversa:", err));
  }, []);

  useEffect(() => {
    fimRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensagens, carregando]);

  async function enviar() {
    const texto = input.trim();
    if (!texto || carregando) return;

    setInput("");
    setMensagens((prev) => [...prev, { role: "user", conteudo: texto }]);
    setCarregando(true);

    try {
      const res = await api.post("/api/chat/pergunta/", {
        conversa_id: conversaId,
        question: texto,
      });
      setMensagens((prev) => [
        ...prev,
        {
          role: "assistant",
          conteudo: res.data.answer,
          fontes: res.data.fontes ?? [],
        },
      ]);
    } catch {
      setMensagens((prev) => [
        ...prev,
        {
          role: "assistant",
          conteudo: "Não foi possível obter uma resposta. Tente novamente.",
          fontes: [],
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

  return (
    <div className="chatArea">
      <div className="mensagens">
        {mensagens.length === 0 ? (
          <div className="placeholder">
            <h2>Como posso ajudar?</h2>
          </div>
        ) : (
          <div className="listaMensagens">
            {mensagens.map((msg, i) => (
              <div key={i} className={`bolha ${msg.role}`}>
                <div className="textoBolha">{msg.conteudo}</div>
                {msg.fontes && msg.fontes.length > 0 && (
                  <div className="fontesArea">
                    <span className="fontesTitulo">Fontes:</span>
                    {msg.fontes.map((fonte) => (
                      <span key={fonte.id} className="fonteTag">
                        {fonte.nome}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

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
          <button
            className="botaoEnviar"
            onClick={enviar}
            disabled={carregando || !input.trim()}
          >
            <img src={enviarIcon} alt="Enviar" />
          </button>
        </div>
      </div>
    </div>
  );
}
