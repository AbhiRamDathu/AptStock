import React, { useState } from "react";

const VOICE_SERVER_URL = "https://aptstock.onrender.com/api/voice";

export default function VoiceAgent() {
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("Ready");
  const [transcript, setTranscript] = useState("");

  const startVoiceAgent = async () => {
    try {
      setStatus("Connecting...");

      const response = await fetch(
        `${VOICE_SERVER_URL}/token`
      );

      if (!response.ok) {
        throw new Error("Could not get voice token");
      }

      const { token } = await response.json();

      const ws = new WebSocket(
        `wss://agents.assemblyai.com/v1/ws?token=${token}`
      );

      ws.onopen = () => {
        setConnected(true);
        setStatus("Listening...");

        ws.send(
          JSON.stringify({
            type: "session.update",
            session: {
              system_prompt:
                "You are AptStock's voice assistant for supermarket inventory planning. " +
                "Help supermarket owners understand sales, inventory, stock alerts, " +
                "forecasting, and replenishment recommendations. " +
                "Keep responses short, clear, practical, and conversational.",

              greeting:
                "Hi, I'm AptStock Assistant. How can I help you with your supermarket inventory today?",

              output: {
                voice: "anna"
              }
            }
          })
        );
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "transcript.user") {
          setTranscript(`You: ${message.text}`);
        }

        if (message.type === "transcript.agent") {
          setTranscript(`AptStock: ${message.text}`);
        }

        if (message.type === "session.error") {
          console.error(message);
          setStatus("Voice error");
        }
      };

      ws.onclose = () => {
        setConnected(false);
        setStatus("Disconnected");
      };

      ws.onerror = () => {
        setStatus("Connection error");
      };

    } catch (error) {
      console.error("Voice agent error:", error);
      setStatus("Unable to connect");
    }
  };

  return (
    <div
      style={{
        padding: "20px",
        borderRadius: "16px",
        background: "#111827",
        color: "white",
        margin: "20px 0"
      }}
    >
      <h3>🎙️ AptStock Voice Assistant</h3>

      <p>{status}</p>

      {transcript && (
        <div
          style={{
            padding: "12px",
            marginBottom: "12px",
            background: "#1f2937",
            borderRadius: "10px"
          }}
        >
          {transcript}
        </div>
      )}

      <button
        onClick={startVoiceAgent}
        disabled={connected}
        style={{
          padding: "12px 20px",
          borderRadius: "10px",
          border: "none",
          cursor: connected ? "default" : "pointer"
        }}
      >
        {connected ? "🎙️ Listening..." : "🎙️ Talk to AptStock"}
      </button>
    </div>
  );
}