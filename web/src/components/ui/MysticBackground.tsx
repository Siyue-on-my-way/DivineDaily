import { motion } from 'framer-motion';

export const MysticBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-[var(--color-deep-void)]">
      {/* Nebula Gradients */}
      <motion.div 
        className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-[var(--color-nebula-purple)] opacity-10 blur-[120px]"
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.1, 0.15, 0.1], 
        }}
        transition={{ 
          duration: 10, 
          repeat: Infinity,
          ease: "easeInOut" 
        }}
      />
      
      <motion.div 
        className="absolute top-[40%] -right-[10%] w-[40%] h-[60%] rounded-full bg-[var(--color-ethereal-gold)] opacity-5 blur-[100px]"
        animate={{ 
          scale: [1, 1.1, 1],
          opacity: [0.05, 0.08, 0.05],
        }}
        transition={{ 
          duration: 15, 
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2
        }}
      />

      <motion.div 
        className="absolute -bottom-[20%] left-[20%] w-[60%] h-[40%] rounded-full bg-blue-900 opacity-10 blur-[120px]"
        animate={{ 
          scale: [1, 1.3, 1],
          opacity: [0.1, 0.12, 0.1],
        }}
        transition={{ 
          duration: 12, 
          repeat: Infinity,
          ease: "easeInOut",
          delay: 5
        }}
      />

      {/* Stars Overlay (Optional: SVG or Canvas could be better for many stars, keeping it simple for now) */}
      <div className="absolute inset-0 opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150 mix-blend-overlay"></div>
    </div>
  );
};
