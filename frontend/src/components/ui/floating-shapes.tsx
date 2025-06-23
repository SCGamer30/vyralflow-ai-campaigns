import { motion } from "framer-motion";

export function FloatingShapes() {
  return (
    <div className="fixed inset-0 pointer-events-none -z-5 overflow-hidden">
      {/* 3D Glass-like sphere inspired by the reference image */}
      <motion.div
        className="absolute top-1/4 right-1/4 w-64 h-64"
        animate={{
          rotateY: [0, 360],
          rotateX: [0, 15, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        <div className="relative w-full h-full">
          {/* Main glass sphere */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-500/20 via-purple-500/30 to-amber-500/20 backdrop-blur-sm border border-pink-300/20" />
          
          {/* Inner glow */}
          <div className="absolute inset-4 rounded-full bg-gradient-to-br from-pink-400/30 via-purple-400/40 to-amber-400/30 backdrop-blur-lg" />
          
          {/* Highlight */}
          <div className="absolute top-6 left-6 w-20 h-20 rounded-full bg-white/20 blur-md" />
          
          {/* Bottom shadow */}
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-32 h-8 bg-black/20 rounded-full blur-xl" />
        </div>
      </motion.div>

      {/* Floating geometric shapes */}
      <motion.div
        className="absolute top-1/3 left-1/4 w-16 h-16 border-2 border-pink-400/30 rotate-45"
        animate={{
          rotate: [45, 405],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute bottom-1/3 right-1/3 w-12 h-12 bg-gradient-to-br from-amber-400/20 to-yellow-400/20 rounded-full"
        animate={{
          y: [0, -20, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute top-1/2 left-1/6 w-8 h-8 bg-gradient-to-br from-purple-400/30 to-pink-400/30"
        style={{ clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)" }}
        animate={{
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "linear",
        }}
      />

      {/* Additional smaller floating elements */}
      {Array.from({ length: 5 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-pink-400/40 rounded-full"
          style={{
            left: `${20 + i * 15}%`,
            top: `${30 + i * 10}%`,
          }}
          animate={{
            y: [0, -15, 0],
            opacity: [0.4, 0.8, 0.4],
          }}
          transition={{
            duration: 4 + i,
            delay: i * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}