import {z} from 'zod';

export const captionWordSchema = z.object({word: z.string(), startFrame: z.number(), endFrame: z.number()});
export const captionCueSchema = z.object({startFrame: z.number(), endFrame: z.number(), words: z.array(captionWordSchema)});
export const beatSchema = z.object({id: z.string(), clip: z.string(), durationFrames: z.number()});
export const episodeSchema = z.object({
  fps: z.number(), width: z.number(), height: z.number(),
  beats: z.array(beatSchema),
  captions: z.array(captionCueSchema),
});
export type Episode = z.infer<typeof episodeSchema>;
