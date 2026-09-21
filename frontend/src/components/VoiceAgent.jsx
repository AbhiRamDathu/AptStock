import React, { useRef, useState } from "react";

const VOICE_SERVER_URL = "https://aptstock.onrender.com/api/voice";
const SAMPLE_RATE = 24000;

export default function VoiceAgent() {
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("Ready");
  const [transcript, setTranscript] = useState("");

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
          1024,
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

        if (ws.bufferedAmount < 256000) {
          ws.send(
            JSON.stringify({
              type: "input.audio",
              audio: base64Audio
            })
          );
        }
      };

      setStatus("Listening...");
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
                 "You are AptStock's voice assistant for supermarket inventory planning. " +
                  "You have access to a live inventory tool called get_inventory_alerts. " +
                  "Whenever the user asks about inventory alerts, stock alerts, products needing attention, " +
                  "or current inventory for a store, you MUST call get_inventory_alerts using the store name. " +
                  "Never say that you cannot access uploaded files, databases, or inventory data. " +
                  "If the store name is missing, ask the user for the store name. " +
                  "After receiving the tool result, explain the result clearly and briefly. " +
                  "Keep responses short, practical, and conversational.",

              greeting:
                "Hi, I'm AptStock Assistant. How can I help you with your supermarket inventory today?",

              output: {
                voice: "anna"
              },
              tools: [
                {
                  type: "function",
                  name: "get_inventory_alerts",
                  description:
                    "Get current inventory alerts and products that may need attention for the selected store.",
                  parameters: {
                    type: "object",
                    properties: {
                      store: {
                        type: "string",
                        description: "The supermarket store name"
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
              pendingToolsRef.current.push({
                call_id: message.call_id,
                result: null,
                arguments: message.arguments || {}
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

            return;
          }

          if (
            message.type ===
            "reply.audio"
          ) {
            // AssemblyAI sends audio in `data`
            await playReplyAudio(
              message.data
            );

            return;
          }

          if (message.type === "tool.call") {
            const store = message.arguments?.store;

            fetch(
              `${VOICE_SERVER_URL.replace("/api/voice", "")}/api/inventory-alerts?store=${encodeURIComponent(store)}`
            )
              .then((res) => res.json())
              .then((result) => {
                ws.send(
                  JSON.stringify({
                    type: "tool.result",
                    call_id: message.call_id,
                    result: JSON.stringify(result),
                  })
                );
              })
              .catch((error) => {
                ws.send(
                  JSON.stringify({
                    type: "tool.result",
                    call_id: message.call_id,
                    result: JSON.stringify({
                      error: error.message,
                    }),
                  })
                );
              });

            return;
          }

          if (message.type === "reply.done") {
            if (message.status === "interrupted") {
              pendingToolsRef.current = [];
              flushPlayback();
              return;
            }

            for (const tool of pendingToolsRef.current) {
              if (tool.result !== null) continue;

              try {
                const store = tool.arguments?.store;

                if (!store) {
                  tool.result = {
                    error: "Store name is required"
                  };
                  continue;
                }

                const token = localStorage.getItem("token");

                const response = await fetch(
                  `${VOICE_SERVER_URL.replace("/api/voice", "")}/api/inventory-alerts?store=${encodeURIComponent(store)}`,
                  {
                    headers: {
                      Authorization: `Bearer ${token}`
                    }
                  }
                );

                const result = await response.json();

                tool.result = result;
              } catch (error) {
                console.error("❌ Inventory tool error:", error);

                tool.result = {
                  error: "Unable to retrieve inventory alerts"
                };
              }
            }

            for (const tool of pendingToolsRef.current) {
              ws.send(
                JSON.stringify({
                  type: "tool.result",
                  call_id: tool.call_id,
                  result: JSON.stringify(tool.result)
                })
              );
            }

            pendingToolsRef.current = [];

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

            return;
          }

          if (
            message.type ===
            "input.speech.stopped"
          ) {
            console.log(
              "🎤 Speech ended"
            );

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
    <div
      style={{
        padding: "20px",
        borderRadius: "16px",
        background: "#111827",
        color: "white",
        margin: "20px 0"
      }}
    >
      <h3>
        🎙️ AptStock Voice Assistant
      </h3>

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

      {!connected ? (
        <button
          onClick={startVoiceAgent}
          style={{
            padding: "12px 20px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer"
          }}
        >
          🎙️ Talk to AptStock
        </button>
      ) : (
        <button
          onClick={stopVoiceAgent}
          style={{
            padding: "12px 20px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer"
          }}
        >
          🛑 Stop
        </button>
      )}
    </div>
  );
}