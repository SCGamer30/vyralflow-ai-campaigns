import { motion } from "framer-motion";
import { useEffect, useRef } from "react";

export function AnimatedBeam({
  className = "",
  duration = 15,
  delay = 0,
  pathColor = "rgba(244, 114, 182, 0.6)",
  gradientStartColor = "#f472b6",
  gradientStopColor = "#fbbf24",
}: {
  className?: string;
  duration?: number;
  delay?: number;
  pathColor?: string;
  gradientStartColor?: string;
  gradientStopColor?: string;
}) {
  const pathRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    if (pathRef.current) {
      const pathLength = pathRef.current.getTotalLength();
      pathRef.current.style.strokeDasharray = `${pathLength}`;
      pathRef.current.style.strokeDashoffset = `${pathLength}`;
    }
  }, []);

  return (
    <div className={`absolute inset-0 ${className}`}>
      <svg
        className="absolute inset-0 h-full w-full"
        width="100%"
        height="100%"
        viewBox="0 0 400 400"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient
            id={`beam-gradient-${delay}`}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop offset="0%" stopColor={gradientStartColor} />
            <stop offset="100%" stopColor={gradientStopColor} />
          </linearGradient>
        </defs>
        <motion.path
          ref={pathRef}
          d="M50 50 Q 200 100 350 50 T 350 350 Q 200 300 50 350 T 50 50"
          stroke={`url(#beam-gradient-${delay})`}
          strokeWidth="2"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{
            duration,
            delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        {/* Glowing effect */}
        <motion.path
          d="M50 50 Q 200 100 350 50 T 350 350 Q 200 300 50 350 T 50 50"
          stroke={pathColor}
          strokeWidth="6"
          fill="none"
          filter="blur(4px)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: [0, 1, 0] }}
          transition={{
            duration: duration * 0.8,
            delay: delay + 0.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </svg>
    </div>
  );
}

export function BeamContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative">
      <AnimatedBeam delay={0} />
      <AnimatedBeam delay={5} />
      <AnimatedBeam delay={10} />
      {children}
    </div>
  );
}