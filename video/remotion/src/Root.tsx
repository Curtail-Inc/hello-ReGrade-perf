import {Composition} from 'remotion';
import {Video} from './Video';
import {episodeSchema} from './schema';

const sample = {fps: 24, width: 1920, height: 1080,
  beats: [{id: 'a', clip: '01-cold-open.mp4', durationFrames: 48}], captions: []};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Video" component={Video} schema={episodeSchema}
    fps={24} width={1920} height={1080} durationInFrames={1} defaultProps={sample}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.max(1, props.beats.reduce((a, b) => a + b.durationFrames, 0)),
      fps: props.fps, width: props.width, height: props.height,
    })}
  />
);
