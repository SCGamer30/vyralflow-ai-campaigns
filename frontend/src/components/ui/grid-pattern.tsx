import { motion } from "framer-motion";

export function GridPattern({
  width = 40,
  height = 40,
  x = -1,
  y = -1,
  strokeDasharray = 0,
  className,
  ...props
}: {
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  strokeDasharray?: number;
  className?: string;
  [key: string]: any;
}) {
  const id = `grid-${Math.random()}`;
  
  return (
    <svg
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 h-full w-full fill-gray-400/30 stroke-gray-400/30 ${className}`}
      {...props}
    >
      <defs>
        <pattern
          id={id}
          width={width}
          height={height}
          patternUnits="userSpaceOnUse"
          x={x}
          y={y}
        >
          <path
            d={`M.5 ${height}V.5H${width}`}
            fill="none"
            strokeDasharray={strokeDasharray}
          />
        </pattern>
      </defs>
      <rect width="100%" height="100%" strokeWidth={0} fill={`url(#${id})`} />
    </svg>
  );
}

export function AnimatedGridPattern({ 
  className = "",
  maxOpacity = 0.5,
  duration = 4,
  repeatDelay = 0.5,
  ...props 
}: {
  className?: string;
  maxOpacity?: number;
  duration?: number;
  repeatDelay?: number;
  [key: string]: any;
}) {
  return (
    <motion.div
      className={`absolute inset-0 ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: [0, maxOpacity, 0] }}
      transition={{
        duration,
        repeat: Infinity,
        repeatDelay,
        ease: "easeInOut",
      }}
    >
      <GridPattern {...props} />
    </motion.div>
  );
}