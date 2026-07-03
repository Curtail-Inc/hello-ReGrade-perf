import {expect, test} from 'vitest';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {existsSync} from 'node:fs';
import path from 'path';

test('Video composition renders a still without throwing', async () => {
  // publicDir must be set at bundle time, not renderStill time (renderStill() has no
  // publicDir option); clips live in ../../capture at build time.
  const serveUrl = await bundle({
    entryPoint: path.join(__dirname, '../src/index.ts'),
    publicDir: path.join(__dirname, '../../capture'),
  });
  const props = {fps: 24, width: 1920, height: 1080,
    beats: [{id: 'a', clip: '01-cold-open.mp4', durationFrames: 48}],
    captions: [{startFrame: 0, endFrame: 48, words: [{word: 'Hello', startFrame: 0, endFrame: 24}, {word: 'world', startFrame: 24, endFrame: 48}]}]};
  const composition = await selectComposition({serveUrl, id: 'Video', inputProps: props});
  const out = path.join(__dirname, 'still.png');
  await renderStill({composition, serveUrl, output: out, inputProps: props, frame: 0});
  expect(existsSync(out)).toBe(true);
}, 120000);
