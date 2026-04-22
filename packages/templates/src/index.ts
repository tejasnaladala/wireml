import type { GraphJSON } from '@wireml/nodes';
import imageClassifier from './image-classifier.json' assert { type: 'json' };
import soundClassifier from './sound-classifier.json' assert { type: 'json' };
import poseClassifier from './pose-classifier.json' assert { type: 'json' };
import zeroShotClip from './zero-shot-clip.json' assert { type: 'json' };

export interface TemplateMeta {
  slug: string;
  title: string;
  subtitle: string;
  tags: string[];
  graph: GraphJSON;
}

export const TEMPLATES: readonly TemplateMeta[] = [
  {
    slug: 'image-classifier',
    title: 'Image classifier',
    subtitle: 'Webcam → CLIP → Linear head → live preview. The canonical TM experience.',
    tags: ['beginner', 'image', 'webcam'],
    graph: imageClassifier as GraphJSON,
  },
  {
    slug: 'sound-classifier',
    title: 'Sound classifier',
    subtitle: 'Microphone → Whisper encoder → k-NN → live preview.',
    tags: ['beginner', 'audio', 'mic'],
    graph: soundClassifier as GraphJSON,
  },
  {
    slug: 'pose-classifier',
    title: 'Pose classifier',
    subtitle: 'Webcam → MediaPipe Pose → Linear head → live preview.',
    tags: ['beginner', 'pose', 'webcam'],
    graph: poseClassifier as GraphJSON,
  },
  {
    slug: 'zero-shot-clip',
    title: 'Zero-shot classifier',
    subtitle: 'No training required — describe your classes in words using CLIP.',
    tags: ['advanced', 'image', 'zero-shot'],
    graph: zeroShotClip as GraphJSON,
  },
] as const;

export function getTemplate(slug: string): TemplateMeta | undefined {
  return TEMPLATES.find((t) => t.slug === slug);
}
