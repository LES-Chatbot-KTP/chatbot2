import { useState, useEffect } from "react";
import api from "../services/api.jsx";
import Sidebar from "../components/Sidebar.jsx";
import ReactMarkdown from "react-markdown";
import { authService } from "../services/authService";

export default function Historico() {
  const [conversas, setConversas] = useState([]);
  const [conversaSelecionada, setConversaSelecionada] = useState(null);
  const [mensagens, setMensagens] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      setLoading(false);
      setConversas([]);
      return;
    }

    // Busca a lista de conversas (Issue 3)
    api.get("/api/chat/historico/periodo/")
      .then(res => {
        setConversas(res.data.conversas);
        setLoading(false);
      })
      .catch(err => { console.error(err); setLoading(false); });
  }, []);

  const carregarChat = (id) => {
    setConversaSelecionada(id);
    api.get(`/api/chat/${id}/historico/`)
      .then(res => setMensagens(res.data.mensagens))
      .catch(err => console.error(err));
  };

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw", backgroundColor: "#1c1c1c", color: "#ffffff" }}>
      <Sidebar tipo="admin" />
      
      {/* Lista de Conversas Esquerda */}
      <div style={{ width: "300px", borderRight: "1px solid #333", overflowY: "auto", padding: "20px" }}>
        <h2 style={{ fontSize: "1.2rem", marginBottom: "20px" }}>Conversas Recentes</h2>
        {loading ? <p>Carregando...</p> : conversas.map(c => (
          <div key={c.id} onClick={() => carregarChat(c.id)} 
               style={{ padding: "12px", cursor: "pointer", backgroundColor: conversaSelecionada === c.id ? "#333" : "transparent", borderRadius: "8px", marginBottom: "8px", border: "1px solid #444" }}>
            <strong>{c.titulo || `Chat #${c.id}`}</strong><br/>
            <small style={{ color: "#aaa" }}>{new Date(c.iniciada_em).toLocaleString('pt-BR')}</small>
          </div>
        ))}
      </div>

      {/* Conteúdo da Conversa Direita */}
      <div style={{ flex: 1, padding: "40px", overflowY: "auto" }}>
        {conversaSelecionada ? (
          <div style={{ maxWidth: "800px", margin: "0 auto" }}>
            <h3>{conversas.find(c => c.id === conversaSelecionada)?.titulo || `Mensagens do Chat #${conversaSelecionada}`}</h3>
            {mensagens.map((m, i) => (
              <div key={i} style={{ marginBottom: "20px", padding: "15px", borderRadius: "10px", backgroundColor: m.role === "user" ? "#2c2f33" : "#444" }}>
                <span style={{ color: m.role === "user" ? "#4caf50" : "#2196f3", fontWeight: "bold" }}>
                  {m.role === "user" ? "Você:" : "Bot:"}
                </span>
                <div style={{ marginTop: "10px" }}><ReactMarkdown>{m.conteudo_original}</ReactMarkdown></div>
              </div>
            ))}
          </div>
        ) : <p style={{ textAlign: "center", marginTop: "20%" }}>Selecione uma conversa ao lado para ver o histórico.</p>}
      </div>
    </div>
  );
}