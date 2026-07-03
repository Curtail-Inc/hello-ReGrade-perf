// ABOUTME: Subtle animated backdrop for the brand + outro cards.
// ABOUTME: A slowly drifting faint-red glow over a whisper dot-grid — premium, not busy.
import {AbsoluteFill, useCurrentFrame} from 'remotion';

export const CardBackdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const x = 50 + 22 * Math.sin(frame / 90);
  const y = 46 + 14 * Math.cos(frame / 120);
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at ${x}% ${y}%, rgba(224,0,31,0.16), transparent 55%)`}}>
      <AbsoluteFill style={{
        backgroundImage: 'radial-gradient(rgba(255,255,255,0.09) 1.5px, transparent 1.5px)',
        backgroundSize: '38px 38px',
      }} />
    </AbsoluteFill>
  );
};
