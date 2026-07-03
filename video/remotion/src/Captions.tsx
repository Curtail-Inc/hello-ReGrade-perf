import {useCurrentFrame} from 'remotion';
import {Episode} from './schema';
import {RED} from './theme';

type Cues = Episode['captions'];

function activeCue(cues: Cues, frame: number): number {
  for (let i = 0; i < cues.length; i++) if (frame >= cues[i].startFrame && frame < cues[i].endFrame) return i;
  return -1;
}

export const Captions: React.FC<{captions: Cues}> = ({captions}) => {
  const frame = useCurrentFrame();
  const idx = activeCue(captions, frame);
  if (idx < 0) return null;
  return (
    <div style={{position: 'absolute', bottom: 88, width: '100%', textAlign: 'center',
      fontFamily: 'Inter, system-ui, sans-serif', fontSize: 52, fontWeight: 700}}>
      <span style={{background: 'rgba(0,0,0,0.62)', padding: '12px 28px', borderRadius: 14,
        border: '1px solid rgba(255,255,255,0.08)', color: 'white', boxDecorationBreak: 'clone',
        WebkitBoxDecorationBreak: 'clone'}}>
        {captions[idx].words.map((w, i) => {
          const spoken = frame >= w.startFrame;
          const speaking = spoken && frame < w.endFrame;
          return (
            <span key={i} style={{
              color: speaking ? RED : 'white', opacity: spoken ? 1 : 0.4,
              display: 'inline-block', transform: speaking ? 'scale(1.08)' : 'none',
              transition: 'none', margin: '0 0.22em'}}>
              {w.word}
            </span>
          );
        })}
      </span>
    </div>
  );
};
