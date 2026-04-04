
let socket = null;

export function connectWS(onMessage) {
  const url = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

  socket = new WebSocket(url);

 
  socket.onopen = () => {
    console.log("✅ WebSocket connected");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data); // Dashboard ko data pass karo
    } catch (error) {
      console.error("WS message parse error:", error);
    }
  };

 
  socket.onerror = (error) => {
    console.error("❌ WebSocket error:", error);
  };


  socket.onclose = () => {
    console.log("🔄 WebSocket closed, reconnecting in 3s...");
    setTimeout(() => connectWS(onMessage), 3000);
  };
}


export function disconnectWS() {
  if (socket) {
    socket.close();
    socket = null;
    console.log("WebSocket disconnected");
  }
}


export function sendMessage(data) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  } else {
    console.warn("WebSocket not connected");
  }
}
