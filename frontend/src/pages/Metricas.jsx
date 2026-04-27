import { useState, useEffect } from "react";
import api from "../services/api.jsx";
import Sidebar from "../components/Sidebar.jsx";

export default function Metricas() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/chat/metricas/")
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Erro ao buscar métricas", err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw", backgroundColor: "#1c1c1c", color: "#ffffff", overflow: "hidden" }}>
      {/* Renderiza o menu lateral bonitão */}
      <Sidebar tipo="admin" />
      
      {/* Conteúdo Principal */}
      <div style={{ flex: 1, padding: "40px", overflowY: "auto" }}>
        <h1 style={{ borderBottom: "1px solid #333", paddingBottom: "15px", marginTop: 0 }}>📊 Métricas de Uso</h1>
        
        {loading ? (
          <p style={{ color: "#a0a0a0" }}>Carregando dados do servidor...</p>
        ) : !data ? (
          <p style={{ color: "#ff6b6b" }}>Erro ao carregar métricas. Verifique se o backend está rodando.</p>
        ) : (
          <>
            {/* GRID DOS CARDS */}
            <div style={{ display: "flex", gap: "20px", marginTop: "30px", flexWrap: "wrap" }}>
              <div style={{ flex: "1 1 250px", backgroundColor: "#2c2f33", padding: "25px", borderRadius: "12px", textAlign: "center", border: "1px solid #444" }}>
                <h3 style={{ color: "#a0a0a0", margin: "0 0 15px 0", textTransform: "uppercase", fontSize: "0.9rem" }}>Total de Conversas</h3>
                <p style={{ fontSize: "3.5rem", margin: 0, color: "#4caf50", fontWeight: "bold" }}>{data.total_conversas}</p>
              </div>
              
              <div style={{ flex: "1 1 250px", backgroundColor: "#2c2f33", padding: "25px", borderRadius: "12px", textAlign: "center", border: "1px solid #444" }}>
                <h3 style={{ color: "#a0a0a0", margin: "0 0 15px 0", textTransform: "uppercase", fontSize: "0.9rem" }}>Total de Mensagens</h3>
                <p style={{ fontSize: "3.5rem", margin: 0, color: "#4caf50", fontWeight: "bold" }}>{data.total_mensagens}</p>
              </div>
              
              <div style={{ flex: "1 1 250px", backgroundColor: "#2c2f33", padding: "25px", borderRadius: "12px", textAlign: "center", border: "1px solid #444" }}>
                <h3 style={{ color: "#a0a0a0", margin: "0 0 15px 0", textTransform: "uppercase", fontSize: "0.9rem" }}>Média de Notas</h3>
                <p style={{ fontSize: "3.5rem", margin: 0, color: "#4caf50", fontWeight: "bold" }}>{data.media_notas}</p>
              </div>
            </div>

            {/* SESSÃO DE FEEDBACKS */}
            <div style={{ marginTop: "30px", backgroundColor: "#2c2f33", padding: "25px", borderRadius: "12px", maxWidth: "400px", border: "1px solid #444" }}>
              <h2 style={{ marginTop: 0, marginBottom: "20px", fontSize: "1.2rem" }}>Feedback dos Usuários</h2>
              
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "1.2rem", padding: "10px 0", borderBottom: "1px solid #444" }}>
                <span>👍 Positivos</span> 
                <strong style={{ color: "#4caf50" }}>{data.feedbacks_positivos}</strong>
              </div>
              
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "1.2rem", padding: "15px 0 0 0" }}>
                <span>👎 Negativos</span> 
                <strong style={{ color: "#ff6b6b" }}>{data.feedbacks_negativos}</strong>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}