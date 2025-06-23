import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface Meteor {
  id: number;
  delay: number;
  duration: number;
  left: number;
  top: number;
  size: number;
}

export function Meteors({ number = 20 }: { number?: number }) {
  const [meteors, setMeteors] = useState<Meteor[]>([]);

  useEffect(() => {
    const meteorArray: Meteor[] = Array.from({ length: number }, (_, i) => ({
      id: i,
      delay: Math.random() * 20,
      duration: Math.random() * 8 + 2,
      left: Math.random() * 100,
      top: Math.random() * 100,
      size: Math.random() * 2 + 1,
    }));
    setMeteors(meteorArray);
  }, [number]);

  return (
    <div className="absolute inset-0 overflow-hidden">
      {meteors.map((meteor) => (
        <motion.div
          key={meteor.id}
          className="absolute"
          style={{
            left: `${meteor.left}%`,
            top: `${meteor.top}%`,
          }}
          initial={{ x: -200, y: -200, opacity: 0 }}
          animate={{
            x: [0, 200],
            y: [0, 200],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: meteor.duration,
            delay: meteor.delay,
            repeat: Infinity,
            repeatDelay: Math.random() * 20 + 10,
            ease: "linear",
          }}
        >
          {/* Meteor head */}
          <div
            className="h-2 w-2 rounded-full bg-gradient-to-r from-pink-400 to-amber-400"
            style={{
              width: `${meteor.size}px`,
              height: `${meteor.size}px`,
              boxShadow: `0 0 ${meteor.size * 2}px rgba(244, 114, 182, 0.8)`,
            }}
          />
          {/* Meteor tail */}
          <div
            className="absolute top-0 left-0 h-px bg-gradient-to-r from-pink-400/80 to-transparent"
            style={{
              width: `${meteor.size * 20}px`,
              transform: "rotate(45deg) translateX(-50%)",
              transformOrigin: "left center",
            }}
          />
        </motion.div>
      ))}
    </div>
  );
}