import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {RED, CANVAS} from './theme';

// The official Agentic Coding Loop (curtail.com/products/regrade), lightly condensed for screen.
const STEPS = [
  'Developer (AI / human) writes new code in the AI agent',
  'The agent uses the ReGrade MCP to replay the previous version’s recorded traffic against the new build',
  'ReGrade records any behavior or performance differences between the two versions',
  'The agent asks ReGrade for the differences and tags each as intended or unintended',
  'Developer uses the difference summary to converge on a fix — faster and more securely',
  'The agent runs tests on the new code (ReGrade records all traffic)',
];

// Reveal fractions across the beat duration (spread so the diagram is never frozen).
const cardFrac = (i: number) => 0.07 + i * 0.135; // 0.07 .. 0.745

const Card: React.FC<{i: number; frame: number; dur: number}> = ({i, frame, dur}) => {
  const start = cardFrac(i) * dur;
  const activeEnd = cardFrac(i + 1) * dur; // "current step" glow until the next reveals
  const opacity = interpolate(frame, [start, start + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lift = interpolate(frame, [start, start + 12], [16, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const active = frame >= start && frame < activeEnd;
  return (
    <div style={{
      flex: 1, borderRadius: 14, padding: '22px 20px', textAlign: 'center',
      background: 'rgba(255,255,255,0.05)',
      border: `1px solid ${active ? RED : 'rgba(255,255,255,0.10)'}`,
      boxShadow: active ? `0 0 26px ${RED}55` : 'none',
      opacity, transform: `translateY(${lift}px)`,
    }}>
      <div style={{
        width: 46, height: 46, borderRadius: 999, background: RED, color: 'white',
        fontWeight: 800, fontSize: 24, display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 12px', boxShadow: active ? `0 0 22px ${RED}` : 'none',
      }}>{i + 1}</div>
      <div style={{color: '#c8ccd6', fontSize: 25, lineHeight: 1.32}}>{STEPS[i]}</div>
    </div>
  );
};

const Arrow: React.FC<{rot: number; frame: number; dur: number; frac: number}> = ({rot, frame, dur, frac}) => {
  const opacity = interpolate(frame, [frac * dur, frac * dur + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{color: RED, fontSize: 40, opacity, flexShrink: 0, transform: `rotate(${rot}deg)`, width: 48, textAlign: 'center'}}>→</div>;
};

export const CycleLoop: React.FC<{durationInFrames: number}> = ({durationInFrames: dur}) => {
  const frame = useCurrentFrame();
  const head = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: CANVAS, fontFamily: 'Inter, system-ui, sans-serif',
      alignItems: 'center', justifyContent: 'center', padding: '0 90px'}}>
      <div style={{opacity: head, marginBottom: 30, color: RED, fontWeight: 800, fontSize: 34}}>The Agentic Coding Loop</div>

      <div style={{width: '100%', maxWidth: 1680}}>
        {/* top row: 1 → 2 → 3 */}
        <div style={{display: 'flex', alignItems: 'stretch', gap: 14, marginBottom: 8}}>
          <Card i={0} frame={frame} dur={dur} /><Arrow rot={0} frame={frame} dur={dur} frac={cardFrac(1)} />
          <Card i={1} frame={frame} dur={dur} /><Arrow rot={0} frame={frame} dur={dur} frac={cardFrac(2)} />
          <Card i={2} frame={frame} dur={dur} />
        </div>
        {/* center row: ↑ | Agentic Loop | ↓ */}
        <div style={{display: 'flex', alignItems: 'center', padding: '10px 0'}}>
          <div style={{flex: 1, display: 'flex', justifyContent: 'center'}}><Arrow rot={270} frame={frame} dur={dur} frac={0.9} /></div>
          <div style={{flex: 1, textAlign: 'center', color: RED, fontWeight: 800, fontSize: 30, opacity: head}}>Agentic Loop</div>
          <div style={{flex: 1, display: 'flex', justifyContent: 'center'}}><Arrow rot={90} frame={frame} dur={dur} frac={cardFrac(3)} /></div>
        </div>
        {/* bottom row shows 6 ← 5 ← 4 (flow 4→5→6) */}
        <div style={{display: 'flex', alignItems: 'stretch', gap: 14, marginTop: 8}}>
          <Card i={5} frame={frame} dur={dur} /><Arrow rot={180} frame={frame} dur={dur} frac={cardFrac(5)} />
          <Card i={4} frame={frame} dur={dur} /><Arrow rot={180} frame={frame} dur={dur} frac={cardFrac(4)} />
          <Card i={3} frame={frame} dur={dur} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
