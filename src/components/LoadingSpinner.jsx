export default function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center
                    min-h-64 gap-4">

      {/* Spinning ring */}
      <div className="relative w-12 h-12">
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full
                        border-2 border-white/10" />
        {/* Spinning part */}
        <div className="absolute inset-0 rounded-full
                        border-2 border-transparent
                        border-t-cyan-400
                        animate-spin" />
      </div>

      {/* Message */}
      <div className="text-white/40 text-sm">{message}</div>

    </div>
  );
}
