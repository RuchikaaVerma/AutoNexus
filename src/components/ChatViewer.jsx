// Conversation ka data
const messages = [
  {
    role: "ai",
    who:  "AI Agent",
    time: "9:00 AM",
    text: "Good morning Sarah! Your Honda City's brake pads need service within 7 days. Shall I book you in?",
  },
  {
    role: "human",
    who:  "Sarah Khan",
    time: "9:02 AM",
    text: "Yes please — Wednesday morning works best for me.",
  },
  {
    role: "ai",
    who:  "AI Agent",
    time: "9:03 AM",
    text: "Perfect! Booked for Wednesday 9:00 AM at ABC Auto Service. Confirmation sent! 🎉",
  },
];

export default function ChatViewer() {
  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">
          Customer Engagement
        </h2>
        <span className="text-xs bg-green-500/10 text-green-400
                         border border-green-500/20 px-2 py-0.5 rounded-full
                         font-semibold">
          ✅ Booked
        </span>
      </div>

      {/* Vehicle + Owner info */}
      <div className="bg-gray-800 rounded-lg px-3 py-2 mb-3 
                      flex items-center gap-2">
        <span className="text-base">🚗</span>
        <div>
          <div className="text-xs font-semibold text-white">
            VEH001 — Honda City
          </div>
          <div className="text-xs text-white/40">Sarah Khan</div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex flex-col gap-2 mb-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${
              m.role === "human" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs text-xs rounded-xl px-3 py-2 ${
                m.role === "ai"
                  ? "bg-cyan-500/8 border border-cyan-500/15 rounded-tl-sm"
                  : "bg-purple-500/8 border border-purple-500/15 rounded-tr-sm"
              }`}
            >
              {/* Who + time */}
              <div className="text-white/30 mb-1">
                {m.who} · {m.time}
              </div>
              {/* Message text */}
              <div className="text-white/80 leading-relaxed">
                {m.text}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Appointment confirmation */}
      <div className="bg-green-500/5 border border-green-500/15
                      rounded-lg p-2.5 text-xs text-green-400
                      text-center font-semibold">
        📅 Wednesday · 9:00 AM · ABC Auto Service
      </div>

    </div>
  );
}