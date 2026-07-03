import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {RED, CANVAS} from './theme';
import {CardBackdrop} from './CardBackdrop';

// fade + slide up, starting at delaySec into the beat
const reveal = (frame: number, fps: number, delaySec: number) => {
  const d = delaySec * fps;
  return {
    opacity: interpolate(frame, [d, d + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
    transform: `translateY(${interpolate(frame, [d, d + 12], [20, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}px)`,
  };
};

export const BrandCard: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logoPop = spring({frame, fps, config: {damping: 200}, durationInFrames: 22});
  return (
    <AbsoluteFill style={{backgroundColor: CANVAS, fontFamily: 'Inter, system-ui, sans-serif',
      alignItems: 'center', justifyContent: 'center'}}>
      <CardBackdrop />
      <Img src={staticFile('curtail-logo.png')} style={{width: 440, marginBottom: 60,
        opacity: interpolate(frame, [0, 16], [0, 1], {extrapolateRight: 'clamp'}),
        transform: `scale(${0.92 + 0.08 * logoPop})`}} />

      <div style={{fontSize: 128, fontWeight: 800, letterSpacing: -2, lineHeight: 1, ...reveal(frame, fps, 0.6)}}>
        <span style={{color: RED}}>Re</span><span style={{color: 'white'}}>Grade</span>
        <span style={{color: '#8a8f9e', fontSize: 42, verticalAlign: 'super', marginLeft: 6}}>®</span>
      </div>

      <div style={{fontSize: 38, color: '#b5bac6', marginTop: 22, ...reveal(frame, fps, 1.3)}}>
        catch performance regressions in your API — under real load
      </div>
    </AbsoluteFill>
  );
};
