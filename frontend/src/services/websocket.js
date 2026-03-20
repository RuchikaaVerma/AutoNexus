// WebSocket connection store karne ke liye
let socket = null;

// WebSocket se connect karo
export function connectWS(onMessage) {
  const url = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

  // Naya connection banao
  socket = new WebSocket(url);

  // Connection khula
  socket.onopen = () => {
    console.log("✅ WebSocket connected");
  };

  // Message aaya backend se
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data); // Dashboard ko data pass karo
    } catch (error) {
      console.error("WS message parse error:", error);
    }
  };

  // Error aaya
  socket.onerror = (error) => {
    console.error("❌ WebSocket error:", error);
  };

  // Connection band ho gaya — 3 second baad reconnect karo
  socket.onclose = () => {
    console.log("🔄 WebSocket closed, reconnecting in 3s...");
    setTimeout(() => connectWS(onMessage), 3000);
  };
}

// Connection band karo
export function disconnectWS() {
  if (socket) {
    socket.close();
    socket = null;
    console.log("WebSocket disconnected");
  }
}

// Message bhejo backend ko
export function sendMessage(data) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  } else {
    console.warn("WebSocket not connected");
  }
}
