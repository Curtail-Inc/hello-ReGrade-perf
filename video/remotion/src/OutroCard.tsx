import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {RED, CANVAS} from './theme';
import {CardBackdrop} from './CardBackdrop';

const reveal = (frame: number, fps: number, delaySec: number) => {
  const d = delaySec * fps;
  return {
    opacity: interpolate(frame, [d, d + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
    transform: `translateY(${interpolate(frame, [d, d + 12], [18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}px)`,
  };
};

const PROPS = ['No credit card', 'No expiration', 'Free every month for individual use'];

export const OutroCard: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logoPop = spring({frame, fps, config: {damping: 200}, durationInFrames: 20});
  return (
    <AbsoluteFill style={{backgroundColor: CANVAS, fontFamily: 'Inter, system-ui, sans-serif',
      alignItems: 'center', justifyContent: 'center'}}>
      <CardBackdrop />
      <Img src={staticFile('curtail-logo.png')} style={{width: 360, marginBottom: 54,
        opacity: interpolate(frame, [0, 16], [0, 1], {extrapolateRight: 'clamp'}),
        transform: `scale(${0.92 + 0.08 * logoPop})`}} />

      <div style={{fontSize: 78, fontWeight: 800, letterSpacing: -1, color: 'white', ...reveal(frame, fps, 0.5)}}>
        Start free at <span style={{color: RED}}>curtail.com</span>
      </div>

      <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 30, fontSize: 34, color: '#c8ccd6', ...reveal(frame, fps, 1.2)}}>
        {PROPS.map((p, i) => (
          <span key={p} style={{display: 'flex', alignItems: 'center', gap: 18}}>
            {i > 0 && <span style={{color: RED, fontSize: 22}}>●</span>}
            {p}
          </span>
        ))}
      </div>

      <div style={{fontSize: 30, color: '#7f8493', marginTop: 64, ...reveal(frame, fps, 2.4)}}>
        Try this demo:&nbsp;&nbsp;<span style={{color: '#b5bac6'}}>github.com/Curtail-Inc/hello-ReGrade-perf</span>
      </div>
    </AbsoluteFill>
  );
};
