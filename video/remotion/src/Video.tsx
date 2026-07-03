import {AbsoluteFill, Series, useCurrentFrame, interpolate} from 'remotion';
import {Episode} from './schema';
import {Beat} from './Beat';
import {BrandCard} from './BrandCard';
import {CycleLoop} from './CycleLoop';
import {OutroCard} from './OutroCard';
import {Highlights} from './Highlights';
import {SectionTag} from './SectionTag';
import {Captions} from './Captions';
import {RED, CANVAS} from './theme';

const DIP = 6; // frames each beat fades up/down at its edges — a soft dip through the shared canvas

const BeatFrame: React.FC<{dur: number; children: React.ReactNode}> = ({dur, children}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, DIP, dur - DIP, dur], [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

// Thin position bar along the bottom edge.
const ProgressBar: React.FC<{total: number}> = ({total}) => {
  const frame = useCurrentFrame();
  const pct = Math.min(1, frame / total);
  return <div style={{position: 'absolute', bottom: 0, left: 0, height: 5,
    width: `${pct * 100}%`, background: RED, boxShadow: `0 0 10px ${RED}aa`}} />;
};

// Clean fade to black over the final frames.
const FadeOut: React.FC<{total: number}> = ({total}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [total - 16, total], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (opacity <= 0) return null;
  return <AbsoluteFill style={{backgroundColor: 'black', opacity, pointerEvents: 'none'}} />;
};

export const Video: React.FC<Episode> = ({beats, captions}) => {
  const total = beats.reduce((a, b) => a + Math.max(1, b.durationFrames), 0);
  return (
    <AbsoluteFill style={{backgroundColor: CANVAS}}>
      <Series>
        {beats.map((b) => {
          const dur = Math.max(1, b.durationFrames);
          return (
            <Series.Sequence key={b.id} durationInFrames={dur}>
              <BeatFrame dur={dur}>
                {b.id === 'cold-open' ? (
                  <BrandCard />
                ) : b.id === 'loop' ? (
                  <CycleLoop durationInFrames={dur} />
                ) : b.id === 'outro' ? (
                  <OutroCard />
                ) : (
                  <>
                    <Beat clip={b.clip} />
                    <Highlights beatId={b.id} durationInFrames={dur} />
                    <SectionTag beatId={b.id} />
                  </>
                )}
              </BeatFrame>
            </Series.Sequence>
          );
        })}
      </Series>
      <AbsoluteFill style={{pointerEvents: 'none',
        background: 'radial-gradient(ellipse 78% 78% at 50% 50%, transparent 62%, rgba(0,0,0,0.32) 100%)'}} />
      <ProgressBar total={total} />
      <Captions captions={captions} />
      <FadeOut total={total} />
    </AbsoluteFill>
  );
};
