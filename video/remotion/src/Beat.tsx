import {AbsoluteFill, OffthreadVideo, staticFile} from 'remotion';
export const Beat: React.FC<{clip: string}> = ({clip}) => (
  <AbsoluteFill style={{backgroundColor: '#1e2030'}}>
    <OffthreadVideo src={staticFile(clip)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
  </AbsoluteFill>
);
