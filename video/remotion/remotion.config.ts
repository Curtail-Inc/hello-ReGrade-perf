import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setConcurrency(1);
Config.setChromiumOpenGlRenderer('swiftshader'); // headless / no-GPU safe
