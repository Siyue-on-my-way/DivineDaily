import { useState, useRef, useEffect } from 'react';

interface MagneticCardOptions {
  maxRotation?: number;
  transitionSpeed?: number;
  resetSpeed?: number;
}

export function useMagneticCard(options: MagneticCardOptions = {}) {
  const {
    maxRotation = 10,
    transitionSpeed = 0.1,
    resetSpeed = 0.3
  } = options;

  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const card = cardRef.current;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * maxRotation;
    const rotateY = ((centerX - x) / centerX) * maxRotation;

    setRotation({ x: rotateX, y: rotateY });
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (!cardRef.current || e.touches.length === 0) return;

    const card = cardRef.current;
    const rect = card.getBoundingClientRect();
    const touch = e.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * maxRotation;
    const rotateY = ((centerX - x) / centerX) * maxRotation;

    setRotation({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setRotation({ x: 0, y: 0 });
  };

  const handleTouchEnd = () => {
    setRotation({ x: 0, y: 0 });
  };

  const style = {
    transform: `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`,
    transition: rotation.x === 0 && rotation.y === 0 
      ? `transform ${resetSpeed}s ease-out` 
      : `transform ${transitionSpeed}s ease-out`
  };

  return {
    cardRef,
    style,
    handlers: {
      onMouseMove: handleMouseMove,
      onMouseLeave: handleMouseLeave,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd
    }
  };
}
