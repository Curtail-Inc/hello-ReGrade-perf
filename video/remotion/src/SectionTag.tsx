import {useCurrentFrame, interpolate} from 'remotion';

const RED = '#E0001F';

// Labels each terminal beat with where it sits in the stress-test flow.
type Section = {step?: number; title: string};
const SECTIONS: Record<string, Section> = {
  problem: {title: 'What functional tests miss'},
  setup: {title: 'Same data, different speed'},
  record: {title: 'Capture a baseline'},
  knobs: {title: 'The three load knobs'},
  stress: {title: 'Replay under load'},
  analyze: {title: 'Performance regressions surface'},
  reveal: {title: 'Only under load'},
};

export const SectionTag: React.FC<{beatId: string}> = ({beatId}) => {
  const frame = useCurrentFrame();
  const s = SECTIONS[beatId];
  if (!s) return null;
  const opacity = interpolate(frame, [2, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', top: 30, right: 48, display: 'flex', alignItems: 'center', gap: 13,
      opacity, fontFamily: 'Inter, system-ui, sans-serif',
      background: 'rgba(20,22,34,0.82)', border: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 999, padding: '9px 20px 9px 11px'}}>
      {s.step != null ? (
        <div style={{width: 32, height: 32, borderRadius: 999, background: RED, color: 'white',
          fontWeight: 800, fontSize: 17, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{s.step}</div>
      ) : (
        <div style={{width: 11, height: 11, borderRadius: 999, background: RED, margin: '0 10px'}} />
      )}
      <div style={{color: '#e6e8ee', fontSize: 23, fontWeight: 600}}>{s.title}</div>
      <div style={{color: '#7f8493', fontSize: 19, marginLeft: 4}}>· Stress test</div>
    </div>
  );
};
