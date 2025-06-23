import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface SparkleProps {
  id: number;
  x: number;
  y: number;
  color: string;
  delay: number;
  scale: number;
}

export function Sparkles({ 
  className = "",
  minSize = 10,
  maxSize = 20,
  particleColor = "#FFF",
  particleDensity = 120
}: {
  className?: string;
  minSize?: number;
  maxSize?: number;
  particleColor?: string;
  particleDensity?: number;
}) {
  const [sparkles, setSparkles] = useState<SparkleProps[]>([]);

  useEffect(() => {
    const generateSparkles = () => {
      const newSparkles: SparkleProps[] = [];
      for (let i = 0; i < particleDensity; i++) {
        newSparkles.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          color: particleColor,
          delay: Math.random() * 3,
          scale: Math.random() * (maxSize - minSize) + minSize,
        });
      }
      setSparkles(newSparkles);
    };

    generateSparkles();
  }, [minSize, maxSize, particleColor, particleDensity]);

  return (
    <div className={`absolute inset-0 overflow-hidden ${className}`}>
      {sparkles.map((sparkle) => (
        <motion.div
          key={sparkle.id}
          className="absolute pointer-events-none"
          style={{
            left: `${sparkle.x}%`,
            top: `${sparkle.y}%`,
          }}
          initial={{ scale: 0, rotate: 0 }}
          animate={{
            scale: [0, 1, 0],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 3,
            delay: sparkle.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <svg
            width={sparkle.scale}
            height={sparkle.scale}
            viewBox="0 0 160 160"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M80 0C80 0 84.2846 41.2925 101.496 58.504C118.707 75.7154 160 80 160 80C160 80 118.707 84.2846 101.496 101.496C84.2846 118.707 80 160 80 160C80 160 75.7154 118.707 58.504 101.496C41.2925 84.2846 0 80 0 80C0 80 41.2925 75.7154 58.504 58.504C75.7154 41.2925 80 0 80 0Z"
              fill={sparkle.color}
            />
          </svg>
        </motion.div>
      ))}
    </div>
  );
}