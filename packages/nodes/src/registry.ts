/**
 * The canonical catalog of node schemas. Both runtimes and the UI import
 * this registry. New nodes land here first.
 */

import type { NodeSchema } from './schema.js';

export const NODE_SCHEMAS: readonly NodeSchema[] = [
  // ──────────────────────────── DATA ────────────────────────────
  {
    id: 'data.webcam',
    name: 'Webcam',
    category: 'data',
    description: 'Live camera feed. Captures frames on demand or continuously.',
    inputs: [],
    outputs: [{ name: 'frames', type: 'image', array: true }],
    params: [
      { name: 'captureMode', kind: 'enum', options: ['manual', 'continuous'], default: 'manual' },
      { name: 'width', kind: 'number', default: 224, min: 64, max: 1024 },
      { name: 'height', kind: 'number', default: 224, min: 64, max: 1024 },
    ],
    capability: { web: true },
    executionMode: 'reactive',
    icon: 'Camera',
  },
  {
    id: 'data.upload',
    name: 'Upload Images',
    category: 'data',
    description: 'User-provided image files (drag-drop or file picker).',
    inputs: [],
    outputs: [
      { name: 'images', type: 'image', array: true },
      { name: 'labels', type: 'labels', array: true },
    ],
    params: [
      { name: 'classes', kind: 'json', default: ['class_a', 'class_b'] },
    ],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Upload',
  },
  {
    id: 'data.mic',
    name: 'Microphone',
    category: 'data',
    description: 'Live microphone audio. Captures clips on demand.',
    inputs: [],
    outputs: [{ name: 'clips', type: 'audio', array: true }],
    params: [
      { name: 'sampleRate', kind: 'number', default: 16000 },
      { name: 'durationMs', kind: 'number', default: 2000, min: 250, max: 10000 },
    ],
    capability: { web: true },
    executionMode: 'reactive',
    icon: 'Mic',
  },

  // ──────────────────────────── BACKBONE ────────────────────────────
  {
    id: 'backbone.clip.vit-b-32',
    name: 'CLIP ViT-B/32 (image)',
    category: 'backbone',
    description: 'OpenAI CLIP ViT-B/32 image encoder. 512-d features.',
    inputs: [{ name: 'images', type: 'image', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [{ name: 'normalize', kind: 'boolean', default: true }],
    capability: { web: true, downloadMb: 335 },
    executionMode: 'reactive',
    icon: 'Brain',
  },
  {
    id: 'backbone.clip.text-vit-b-32',
    name: 'CLIP ViT-B/32 (text)',
    category: 'backbone',
    description: 'CLIP text encoder. 512-d features aligned with CLIP image.',
    inputs: [{ name: 'text', type: 'text', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [{ name: 'normalize', kind: 'boolean', default: true }],
    capability: { web: true, downloadMb: 246 },
    executionMode: 'reactive',
    icon: 'Type',
  },
  {
    id: 'backbone.dinov2.small',
    name: 'DINOv2 ViT-S/14',
    category: 'backbone',
    description: 'Meta DINOv2 self-supervised image features. 384-d.',
    inputs: [{ name: 'images', type: 'image', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [],
    capability: { web: true, downloadMb: 88 },
    executionMode: 'reactive',
    icon: 'Eye',
  },
  {
    id: 'backbone.mobilenet.v3',
    name: 'MobileNetV3',
    category: 'backbone',
    description: 'Lightweight mobile-first image backbone. 1280-d features.',
    inputs: [{ name: 'images', type: 'image', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [],
    capability: { web: true, downloadMb: 22 },
    executionMode: 'reactive',
    icon: 'Smartphone',
  },
  {
    id: 'backbone.whisper.tiny',
    name: 'Whisper tiny (encoder)',
    category: 'backbone',
    description: 'Whisper tiny audio encoder. Produces per-frame features.',
    inputs: [{ name: 'audio', type: 'audio', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [],
    capability: { web: true, downloadMb: 75 },
    executionMode: 'reactive',
    icon: 'AudioWaveform',
  },
  {
    id: 'backbone.mediapipe.pose',
    name: 'MediaPipe Pose',
    category: 'backbone',
    description: 'Landmark-based human pose backbone. 132-d features (33 joints × 4).',
    inputs: [{ name: 'images', type: 'image', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [{ name: 'modelComplexity', kind: 'enum', options: ['lite', 'full'], default: 'lite' }],
    capability: { web: true, downloadMb: 12 },
    executionMode: 'reactive',
    icon: 'PersonStanding',
  },
  {
    id: 'backbone.clip.vit-l-14',
    name: 'CLIP ViT-L/14 (image)',
    category: 'backbone',
    description: 'Larger CLIP image encoder. 768-d features, higher accuracy.',
    inputs: [{ name: 'images', type: 'image', array: true }],
    outputs: [{ name: 'features', type: 'features', array: true }],
    params: [{ name: 'normalize', kind: 'boolean', default: true }],
    capability: { localOnly: true, minVramGb: 6, downloadMb: 1700 },
    executionMode: 'reactive',
    icon: 'Brain',
  },

  // ──────────────────────────── HEAD ────────────────────────────
  {
    id: 'head.linear',
    name: 'Linear Classifier',
    category: 'head',
    description: 'Trainable linear head. Soft-max over classes.',
    inputs: [
      { name: 'features', type: 'features', array: true },
      { name: 'labels', type: 'labels', array: true, optional: true },
    ],
    outputs: [{ name: 'model', type: 'model' }],
    params: [
      { name: 'epochs', kind: 'number', default: 50, min: 1, max: 500 },
      { name: 'learningRate', kind: 'number', default: 0.001, min: 1e-5, max: 1, step: 1e-4 },
      { name: 'batchSize', kind: 'number', default: 16, min: 1, max: 256 },
    ],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Calculator',
  },
  {
    id: 'head.knn',
    name: 'k-NN',
    category: 'head',
    description: 'Non-parametric nearest-neighbor classifier. No training required.',
    inputs: [
      { name: 'features', type: 'features', array: true },
      { name: 'labels', type: 'labels', array: true },
    ],
    outputs: [{ name: 'model', type: 'model' }],
    params: [
      { name: 'k', kind: 'number', default: 5, min: 1, max: 50 },
      { name: 'metric', kind: 'enum', options: ['cosine', 'euclidean'], default: 'cosine' },
    ],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Network',
  },
  {
    id: 'head.zeroshot-clip',
    name: 'Zero-Shot CLIP',
    category: 'head',
    description: 'Text-prompted classifier. No labeled data needed — describe classes in words.',
    inputs: [
      { name: 'imageFeatures', type: 'features', array: true },
      { name: 'textFeatures', type: 'features', array: true },
    ],
    outputs: [{ name: 'model', type: 'model' }],
    params: [
      { name: 'temperature', kind: 'number', default: 100, min: 1, max: 1000 },
    ],
    capability: { web: true },
    executionMode: 'reactive',
    icon: 'Sparkles',
  },

  // ──────────────────────────── EVAL ────────────────────────────
  {
    id: 'eval.accuracy',
    name: 'Accuracy',
    category: 'eval',
    description: 'Top-1 accuracy on a held-out split.',
    inputs: [
      { name: 'model', type: 'model' },
      { name: 'features', type: 'features', array: true },
      { name: 'labels', type: 'labels', array: true },
    ],
    outputs: [{ name: 'metrics', type: 'metrics' }],
    params: [
      { name: 'split', kind: 'enum', options: ['val', 'test'], default: 'val' },
    ],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Target',
  },
  {
    id: 'eval.confusion',
    name: 'Confusion Matrix',
    category: 'eval',
    description: 'Per-class confusion matrix.',
    inputs: [
      { name: 'model', type: 'model' },
      { name: 'features', type: 'features', array: true },
      { name: 'labels', type: 'labels', array: true },
    ],
    outputs: [{ name: 'metrics', type: 'metrics' }],
    params: [],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Grid3x3',
  },

  // ──────────────────────────── DEPLOY ────────────────────────────
  {
    id: 'deploy.preview',
    name: 'Live Preview',
    category: 'deploy',
    description: 'Classify a live webcam / mic stream and show class probabilities.',
    inputs: [
      { name: 'model', type: 'model' },
      { name: 'features', type: 'features', array: true },
    ],
    outputs: [],
    params: [
      { name: 'showBars', kind: 'boolean', default: true },
      { name: 'topK', kind: 'number', default: 3, min: 1, max: 10 },
    ],
    capability: { web: true },
    executionMode: 'reactive',
    icon: 'Monitor',
  },
  {
    id: 'deploy.export-onnx',
    name: 'Export ONNX',
    category: 'deploy',
    description: 'Serialize the trained pipeline to ONNX.',
    inputs: [{ name: 'model', type: 'model' }],
    outputs: [],
    params: [
      { name: 'opsetVersion', kind: 'number', default: 17, min: 11, max: 20 },
      { name: 'filename', kind: 'string', default: 'wireml-model.onnx' },
    ],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Download',
  },
  {
    id: 'deploy.share-url',
    name: 'Shareable URL',
    category: 'deploy',
    description: 'Encode the trained classifier into a URL for sharing.',
    inputs: [{ name: 'model', type: 'model' }],
    outputs: [],
    params: [],
    capability: { web: true },
    executionMode: 'triggered',
    icon: 'Link2',
  },
] as const;

/** Look up a schema by id. Throws if the id is unknown. */
export function getSchema(id: string): NodeSchema {
  const schema = NODE_SCHEMAS.find((s) => s.id === id);
  if (!schema) throw new Error(`Unknown node schema: ${id}`);
  return schema;
}

export function getSchemas(ids: readonly string[]): NodeSchema[] {
  return ids.map(getSchema);
}
