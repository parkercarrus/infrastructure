export function GalaxyBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Base gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0a0a1a] via-[#1a0a2e] to-[#0f0a1f] animate-gradient-shift" />
      
      {/* Nebula clouds */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px] animate-nebula-1" />
        <div className="absolute top-2/3 right-1/4 w-[500px] h-[500px] bg-blue-600/15 rounded-full blur-[140px] animate-nebula-2" />
        <div className="absolute bottom-1/4 left-1/2 w-80 h-80 bg-pink-600/10 rounded-full blur-[100px] animate-nebula-3" />
      </div>
      
      {/* Stars layer 1 - small twinkling stars */}
      <div className="absolute inset-0 opacity-60">
        {[...Array(50)].map((_, i) => (
          <div
            key={`star-1-${i}`}
            className="absolute w-[1px] h-[1px] bg-white rounded-full animate-twinkle"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`
            }}
          />
        ))}
      </div>
      
      {/* Stars layer 2 - medium stars */}
      <div className="absolute inset-0 opacity-80">
        {[...Array(30)].map((_, i) => (
          <div
            key={`star-2-${i}`}
            className="absolute w-[2px] h-[2px] bg-white rounded-full animate-twinkle"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>
      
      {/* Shooting stars */}
      <div className="absolute inset-0">
        {[...Array(3)].map((_, i) => (
          <div
            key={`shooting-${i}`}
            className="absolute w-[2px] h-[2px] bg-white rounded-full animate-shooting-star"
            style={{
              top: `${Math.random() * 50}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${i * 8 + Math.random() * 5}s`,
              animationDuration: '2s'
            }}
          />
        ))}
      </div>
      
      {/* Supernova glow */}
      <div className="absolute top-1/3 right-1/3 w-32 h-32 bg-white/30 rounded-full blur-[80px] animate-supernova" />
    </div>
  );
}
