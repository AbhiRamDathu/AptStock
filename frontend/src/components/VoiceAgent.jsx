import React, { useRef, useState } from "react";

const VOICE_SERVER_URL = "https://aptstock.onrender.com/api/voice";
const SAMPLE_RATE = 24000;

export default function VoiceAgent({ dashboardData }) {
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("Ready");
  const [transcript, setTranscript] = useState("");
  const [voiceState, setVoiceState] = useState("idle");

  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const micStreamRef = useRef(null);
  const micSourceRef = useRef(null);
  const processorRef = useRef(null);
  const silentGainRef = useRef(null);
  const pendingToolsRef = useRef([]);

  const playbackContextRef = useRef(null);
  const playbackNextTimeRef = useRef(0);
  const playbackSourcesRef = useRef([]);

  const cleanup = () => {
    try {
      if (processorRef.current) {
        processorRef.current.onaudioprocess = null;
        processorRef.current.disconnect();
      }

      if (micSourceRef.current) {
        micSourceRef.current.disconnect();
      }

      if (silentGainRef.current) {
        silentGainRef.current.disconnect();
      }

      if (micStreamRef.current) {
        micStreamRef.current.getTracks().forEach((track) => track.stop());
      }

      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
    } catch (error) {
      console.warn("Audio cleanup error:", error);
    }

    processorRef.current = null;
    micSourceRef.current = null;
    silentGainRef.current = null;
    micStreamRef.current = null;
    audioContextRef.current = null;

    playbackSourcesRef.current.forEach((source) => {
      try {
        source.stop();
      } catch {}
    });

    playbackSourcesRef.current = [];
    playbackNextTimeRef.current = 0;
  };

  const flushPlayback = () => {
    playbackSourcesRef.current.forEach((source) => {
      try {
        source.stop();
      } catch {}
    });

    playbackSourcesRef.current = [];

    if (playbackContextRef.current) {
      playbackNextTimeRef.current =
        playbackContextRef.current.currentTime;
    }
  };

  const playReplyAudio = async (base64Audio) => {
    try {
      if (!base64Audio) return;

      if (!playbackContextRef.current) {
        playbackContextRef.current = new AudioContext();
      }

      const ctx = playbackContextRef.current;

      if (ctx.state === "suspended") {
        await ctx.resume();
      }

      // Base64 → binary
      const binary = atob(base64Audio);
      const pcm16 = new Int16Array(binary.length / 2);

      for (let i = 0; i < pcm16.length; i++) {
        const low = binary.charCodeAt(i * 2);
        const high = binary.charCodeAt(i * 2 + 1);

        pcm16[i] = low | (high << 8);
      }

      // PCM16 → Float32
      const float32 = new Float32Array(pcm16.length);

      for (let i = 0; i < pcm16.length; i++) {
        float32[i] =
          pcm16[i] < 0
            ? pcm16[i] / 32768
            : pcm16[i] / 32767;
      }

      // AssemblyAI reply audio is 24 kHz mono PCM16.
      const audioBuffer = ctx.createBuffer(
        1,
        float32.length,
        SAMPLE_RATE
      );

      audioBuffer.copyToChannel(float32, 0);

      const source = ctx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(ctx.destination);

      const now = ctx.currentTime;

      if (playbackNextTimeRef.current < now) {
        playbackNextTimeRef.current = now;
      }

      source.start(playbackNextTimeRef.current);

      playbackNextTimeRef.current += audioBuffer.duration;

      playbackSourcesRef.current.push(source);

      source.onended = () => {
        playbackSourcesRef.current =
          playbackSourcesRef.current.filter((s) => s !== source);
      };
    } catch (error) {
      console.error("Reply audio playback error:", error);
    }
  };

  const startMicrophone = async (ws) => {
    try {
      setStatus("Starting microphone...");

      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        });

      micStreamRef.current = stream;

      const audioContext = new AudioContext({
        sampleRate: SAMPLE_RATE
      });

      audioContextRef.current = audioContext;

      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }

      console.log(
        "🎙️ Microphone AudioContext sample rate:",
        audioContext.sampleRate
      );

      const source =
        audioContext.createMediaStreamSource(stream);

      micSourceRef.current = source;

      /*
       * ScriptProcessorNode is used here to keep this implementation
       * self-contained inside VoiceAgent.jsx.
       */
      const processor =
        audioContext.createScriptProcessor(
          2048,
          1,
          1
        );

      processorRef.current = processor;

      // Keep processor alive without sending microphone audio
      // to the speakers.
      const silentGain =
        audioContext.createGain();

      silentGain.gain.value = 0;

      silentGainRef.current = silentGain;

      source.connect(processor);
      processor.connect(silentGain);
      silentGain.connect(audioContext.destination);

      processor.onaudioprocess = (event) => {
        if (
          !ws ||
          ws.readyState !== WebSocket.OPEN
        ) {
          return;
        }

        const input =
          event.inputBuffer.getChannelData(0);

        /*
         * Convert Float32 microphone samples
         * into signed 16-bit PCM little-endian.
         */
        const pcm16 =
          new Int16Array(input.length);

        for (let i = 0; i < input.length; i++) {
          const sample =
            Math.max(-1, Math.min(1, input[i]));

          pcm16[i] =
            sample < 0
              ? sample * 0x8000
              : sample * 0x7fff;
        }

        // Int16Array → binary string → base64
        const bytes = new Uint8Array(
          pcm16.buffer
        );

        let binary = "";

        const chunkSize = 0x8000;

        for (
          let i = 0;
          i < bytes.length;
          i += chunkSize
        ) {
          binary += String.fromCharCode(
            ...bytes.subarray(
              i,
              Math.min(i + chunkSize, bytes.length)
            )
          );
        }

        const base64Audio = btoa(binary);

        if (ws.bufferedAmount < 65536) {
          ws.send(
            JSON.stringify({
              type: "input.audio",
              audio: base64Audio
            })
          );
        }
      };

      setStatus("Listening...");
      setVoiceState("listening");
      console.log("🎙️ Microphone streaming started");
    } catch (error) {
      console.error(
        "❌ Microphone access error:",
        error
      );

      setStatus(
        "Microphone permission required"
      );

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    }
  };

  const startVoiceAgent = async () => {
    try {
      setStatus("Connecting...");
      setTranscript("");

      // Get temporary AssemblyAI token
      const response = await fetch(
        `${VOICE_SERVER_URL}/token`
      );

      if (!response.ok) {
        throw new Error(
          `Token request failed: ${response.status}`
        );
      }

      const { token } =
        await response.json();

      console.log("✅ Voice token received");

      const ws = new WebSocket(
        `wss://agents.assemblyai.com/v1/ws?token=${token}`
      );

      wsRef.current = ws;

      ws.onopen = () => {
        console.log(
          "✅ AssemblyAI WebSocket connected"
        );

        setStatus("Initializing voice agent...");

        ws.send(
          JSON.stringify({
            type: "session.update",
            session: {
              system_prompt:
                 "You are AptStock's AI voice assistant for multi-SKU retailers and stores. " +
                  "Help retailers understand inventory alerts, stock risks, demand forecasts, " +
                  "replenishment recommendations, and products needing attention. " +
                  "You have access to live inventory data through the get_inventory_alerts tool. " +
                  "When asked about current inventory or alerts, use the tool and explain the result. " +
                  "Use the customer's current AptStock store context when available. Do not ask the customer to provide a store name if the application already has a store context. " +
                  "Keep every response short, practical, and conversational.",

              greeting:
                "Hi, I'm AptStock Assistant. How can I help you manage your store inventory today?",

              output: {
                voice: "anna"
              },
              tools: [
                {
                  type: "function",
                  name: "get_inventory_alerts",
                  description:
                    "Get a compact summary of current inventory alerts and products needing attention for the selected store.",
                  parameters: {
                    type: "object",
                    properties: {
                      store: {
                        type: "string",
                        description: "The retailer, store, branch, or location name"
                      }
                    },
                    required: ["store"]
                  }
                }
              ]
            }
          })
        );
      };

      ws.onmessage = async (event) => {
        try {
          const message =
            JSON.parse(event.data);

          console.log(
            "🤖 Voice event:",
            message.type
          );

          if (message.type === "tool.call") {
            console.log("🔧 Tool call:", message);

            if (message.name === "get_inventory_alerts") {
              const compactResult = {
                store: dashboardData?.store || "Current Store",

                status: "connected",

                inventory_count: Array.isArray(dashboardData?.inventory)
                  ? dashboardData.inventory.length
                  : 0,

                alert_count: Array.isArray(dashboardData?.priorityActions)
                  ? dashboardData.priorityActions.length
                  : 0,

                top_alerts: Array.isArray(dashboardData?.priorityActions)
                  ? dashboardData.priorityActions.slice(0, 5)
                  : [],

                forecasts: Array.isArray(dashboardData?.forecasts)
                  ? dashboardData.forecasts.slice(0, 5)
                  : [],

                inventory: Array.isArray(dashboardData?.inventory)
                  ? dashboardData.inventory.slice(0, 10)
                  : []
              };

              console.log(
                "📦 Voice dashboard data:",
                compactResult
              );

    // Queue the tool result.
    // It will be sent after reply.done.
              pendingToolsRef.current.push({
                call_id: message.call_id,
                result: compactResult
              });
            }

            return;
          }

          if (
            message.type ===
            "session.ready"
          ) {
            console.log(
              "✅ AssemblyAI session ready:",
              message.session_id
            );

            setConnected(true);

            // IMPORTANT:
            // Microphone starts only AFTER session.ready.
            await startMicrophone(ws);

            return;
          }

          if (
            message.type ===
            "transcript.user.delta"
          ) {
            setTranscript(
              `You: ${message.text || ""}`
            );

            return;
          }

          if (
            message.type ===
            "transcript.user"
          ) {
            setTranscript(
              `You: ${message.text || ""}`
            );

            return;
          }

          if (
            message.type ===
            "transcript.agent"
          ) {
            setTranscript(
              `AptStock: ${message.text || ""}`
            );
            setVoiceState("speaking");

            return;
          }

          if (
            message.type ===
            "reply.started"
          ) {
            setVoiceState("thinking");
            return;
          }

          if (
            message.type ===
            "reply.audio"
          ) {
            setVoiceState("speaking");
            // AssemblyAI sends audio in `data`
            await playReplyAudio(
              message.data
            );

            return;
          }

          if (message.type === "reply.done") {
            if (message.status === "interrupted") {
              pendingToolsRef.current = [];
              flushPlayback();
            } else if (pendingToolsRef.current.length > 0) {
              for (const tool of pendingToolsRef.current) {
                if (ws.readyState === WebSocket.OPEN) {
                  ws.send(
                    JSON.stringify({
                      type: "tool.result",
                      call_id: tool.call_id,
                      result: JSON.stringify(tool.result)
                    })
                  );
                }
              }

              pendingToolsRef.current = [];
            }

            setVoiceState("listening");
            return;
          }

          if (
            message.type ===
            "session.error"
          ) {
            console.error(
              "❌ AssemblyAI session error:",
              message
            );

            setStatus(
              `Voice error: ${
                message.message ||
                message.code ||
                "Unknown error"
              }`
            );

            return;
          }

          if (
            message.type ===
            "input.speech.started"
          ) {
            console.log(
              "🎤 Speech detected"
            );
            setVoiceState("listening");

            return;
          }

          if (
            message.type ===
            "input.speech.stopped"
          ) {
            console.log(
              "🎤 Speech ended"
            );
            setVoiceState("thinking");

            return;
          }
        } catch (error) {
          console.error(
            "Voice message processing error:",
            error
          );
        }
      };

      ws.onerror = (error) => {
        console.error(
          "❌ Voice WebSocket error:",
          error
        );

        setStatus(
          "Voice connection error"
        );
      };

      ws.onclose = (event) => {
        console.log(
          "🔌 Voice WebSocket closed:",
          event.code,
          event.reason
        );

        cleanup();

        setConnected(false);
        setStatus("Disconnected");
      };
    } catch (error) {
      console.error(
        "❌ Voice agent error:",
        error
      );

      cleanup();

      setConnected(false);
      setStatus(
        error.message ||
        "Unable to connect"
      );
    }
  };

  const stopVoiceAgent = () => {
    console.log(
      "🛑 Stopping voice agent..."
    );

    cleanup();

    if (
      wsRef.current &&
      wsRef.current.readyState ===
        WebSocket.OPEN
    ) {
      wsRef.current.close();
    }

    wsRef.current = null;

    setConnected(false);
    setStatus("Ready");
  };

    return (
       <>
    <style>{`
      @keyframes aptstockPulse {
        0%, 100% {
          box-shadow: 0 0 0 10px rgba(96,165,250,0.10),
                      0 0 35px rgba(96,165,250,0.35);
        }
        50% {
          box-shadow: 0 0 0 18px rgba(96,165,250,0.04),
                      0 0 75px rgba(96,165,250,0.65);
        }
      }
    `}
    </style>
    <div
      style={{
        margin: "24px 0",
        padding: "28px",
        borderRadius: "24px",
        background:
          "linear-gradient(135deg, #0f172a 0%, #111827 55%, #172554 100%)",
        color: "#ffffff",
        boxShadow: "0 18px 50px rgba(15, 23, 42, 0.18)",
        border: "1px solid rgba(255,255,255,0.08)",
        overflow: "hidden",
        position: "relative"
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          marginBottom: "24px"
        }}
      >
        <div>
          <div
            style={{
              fontSize: "12px",
              fontWeight: "700",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "#93c5fd",
              marginBottom: "6px"
            }}
          >
            AptStock Intelligence
          </div>

          <h3
            style={{
              margin: 0,
              fontSize: "24px",
              fontWeight: "700"
            }}
          >
            Voice Assistant
          </h3>

          <p
            style={{
              margin: "6px 0 0",
              color: "#94a3b8",
              fontSize: "14px"
            }}
          >
            Ask about stock risks, alerts, forecasts and replenishment.
          </p>
        </div>

        <div
          style={{
            padding: "7px 12px",
            borderRadius: "999px",
            background: connected
              ? "rgba(34,197,94,0.14)"
              : "rgba(148,163,184,0.12)",
            color: connected ? "#86efac" : "#cbd5e1",
            fontSize: "12px",
            fontWeight: "700",
            whiteSpace: "nowrap"
          }}
        >
          {connected ? "● LIVE" : "● READY"}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "10px 0 24px"
        }}
      >
        <div
          style={{
            width: "116px",
            height: "116px",
            transform:
              voiceState === "listening"
                ? "scale(1.12)"
                : voiceState === "thinking"
                ? "scale(1.05)"
                : voiceState === "speaking"
                ? "scale(1.08)"
                : "scale(1)",
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background:
              "radial-gradient(circle at 35% 30%, #60a5fa, #4f46e5 48%, #312e81 100%)",
            boxShadow:
              voiceState === "listening"
                ? "0 0 0 16px rgba(96,165,250,0.12), 0 0 70px rgba(96,165,250,0.55)"
                : voiceState === "thinking"
                ? "0 0 0 10px rgba(129,140,248,0.10), 0 0 55px rgba(129,140,248,0.45)"
                : voiceState === "speaking"
                ? "0 0 0 14px rgba(34,197,94,0.10), 0 0 65px rgba(34,197,94,0.40)"
                : "0 12px 35px rgba(0,0,0,0.25)",
            transition: "all 0.3s ease",
            animation:
              voiceState === "listening"
                ? "aptstockPulse 1.8s ease-in-out infinite"
                : "none",
                      }}
        >
          <span
            style={{
              fontSize: "42px"
            }}
          >
            🎙️
          </span>
        </div>

        <div
          style={{
            marginTop: "18px",
            fontSize: "16px",
            fontWeight: "600"
          }}
        >
          {status}
        </div>

        <div
          style={{
            marginTop: "5px",
            color: "#94a3b8",
            fontSize: "13px"
          }}
        >
          {connected
            ? "Speak naturally — I'm listening."
            : "Start a conversation with AptStock."}
        </div>
      </div>

      {transcript && (
        <div
          style={{
            marginBottom: "20px",
            padding: "16px 18px",
            borderRadius: "16px",
            background: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.08)"
          }}
        >
          <div
            style={{
              fontSize: "11px",
              fontWeight: "700",
              color: "#93c5fd",
              textTransform: "uppercase",
              letterSpacing: "0.07em",
              marginBottom: "7px"
            }}
          >
            Live conversation
          </div>

          <div
            style={{
              color: "#e2e8f0",
              fontSize: "15px",
              lineHeight: 1.6
            }}
          >
            {transcript}
          </div>
        </div>
      )}

      <div
        style={{
          display: "flex",
          justifyContent: "center"
        }}
      >
        {!connected ? (
          <button
            onClick={startVoiceAgent}
            style={{
              width: "100%",
              maxWidth: "340px",
              padding: "15px 22px",
              borderRadius: "14px",
              border: "none",
              background:
                "linear-gradient(135deg, #6366f1, #4f46e5)",
              color: "#ffffff",
              fontSize: "15px",
              fontWeight: "700",
              cursor: "pointer",
              boxShadow: "0 10px 25px rgba(79,70,229,0.3)"
            }}
          >
            🎙️ Start Voice Assistant
          </button>
        ) : (
          <button
            onClick={stopVoiceAgent}
            style={{
              width: "100%",
              maxWidth: "340px",
              padding: "15px 22px",
              borderRadius: "14px",
              border: "1px solid rgba(248,113,113,0.35)",
              background: "rgba(239,68,68,0.12)",
              color: "#fca5a5",
              fontSize: "15px",
              fontWeight: "700",
              cursor: "pointer"
            }}
          >
            ⏹ Stop Conversation
          </button>
        )}
      </div>
    </div>
    </>
  );
}