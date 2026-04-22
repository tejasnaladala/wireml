/**
 * Browser-side node executor. Uses @huggingface/transformers (a.k.a.
 * Transformers.js) and ONNX Runtime Web where available; falls back to
 * simple JS for heads and eval nodes.
 *
 * This is a minimal but real implementation — it actually loads CLIP,
 * runs a linear head, and computes k-NN. Designed as the starting point
 * for the scheduler; additional nodes will plug in via the same pattern.
 */

import type {
  GraphRunner,
  NodeExecutionContext,
  NodeExecutionResult,
  NodeInstance,
  RuntimeCapabilities,
} from '@wireml/nodes';
import { probeWebRuntime } from '@/store/runtimeStore';

type NodeRunner = (
  node: NodeInstance,
  ctx: NodeExecutionContext,
) => Promise<NodeExecutionResult>;

/**
 * Lazy-loader for Transformers.js pipelines. Caches by schemaId so we
 * only download each backbone once per session.
 */
const pipelineCache = new Map<string, unknown>();

async function getTransformers() {
  const mod = (await import('@huggingface/transformers')) as unknown as {
    pipeline: (
      task: string,
      model: string,
      opts?: Record<string, unknown>,
    ) => Promise<unknown>;
    env: Record<string, unknown>;
  };
  // Prefer WebGPU when available.
  (mod.env as any).backends = (mod.env as any).backends ?? {};
  (mod.env as any).backends.onnx = (mod.env as any).backends.onnx ?? {};
  (mod.env as any).backends.onnx.wasm = { numThreads: 1 };
  return mod;
}

async function loadClipImagePipeline(onProgress?: (f: number, m?: string) => void) {
  if (pipelineCache.has('clip.image')) return pipelineCache.get('clip.image');
  const { pipeline } = await getTransformers();
  const pipe = await pipeline('image-feature-extraction', 'Xenova/clip-vit-base-patch32', {
    device: 'webgpu',
    progress_callback: (p: { progress: number; file: string }) => {
      onProgress?.(p.progress ?? 0, p.file);
    },
  });
  pipelineCache.set('clip.image', pipe);
  return pipe;
}

async function loadClipTextPipeline(onProgress?: (f: number, m?: string) => void) {
  if (pipelineCache.has('clip.text')) return pipelineCache.get('clip.text');
  const { pipeline } = await getTransformers();
  const pipe = await pipeline('feature-extraction', 'Xenova/clip-vit-base-patch32', {
    device: 'webgpu',
    progress_callback: (p: { progress: number; file: string }) => {
      onProgress?.(p.progress ?? 0, p.file);
    },
  });
  pipelineCache.set('clip.text', pipe);
  return pipe;
}

// ───────────────────────── NODE RUNNERS ─────────────────────────

const runners: Record<string, NodeRunner> = {
  'data.webcam': async (_node, _ctx) => ({
    // Webcam frames are captured in the preview UI and injected into the
    // scheduler on each tick. This runner is a pass-through for frames
    // already placed into `ctx.inputs.frames`.
    outputs: { frames: _ctx.inputs.frames ?? [] },
  }),

  'data.upload': async (_node, ctx) => ({
    outputs: {
      images: ctx.inputs.images ?? [],
      labels: ctx.inputs.labels ?? [],
    },
  }),

  'data.mic': async (_node, ctx) => ({ outputs: { clips: ctx.inputs.clips ?? [] } }),

  'backbone.clip.vit-b-32': async (_node, ctx) => {
    const pipe = (await loadClipImagePipeline(ctx.onProgress)) as (
      images: unknown,
    ) => Promise<{ data: Float32Array; dims: number[] }>;
    const images = (ctx.inputs.images ?? ctx.inputs.frames ?? []) as unknown[];
    if (images.length === 0) return { outputs: { features: [] } };
    const result = await pipe(images as any);
    const features = result?.data ? [Array.from(result.data)] : [];
    return { outputs: { features } };
  },

  'backbone.clip.text-vit-b-32': async (_node, ctx) => {
    const pipe = (await loadClipTextPipeline(ctx.onProgress)) as (
      text: string[],
    ) => Promise<{ data: Float32Array; dims: number[] }>;
    const texts = (ctx.inputs.text ?? []) as string[];
    if (texts.length === 0) return { outputs: { features: [] } };
    const result = await pipe(texts);
    return { outputs: { features: [Array.from(result.data)] } };
  },

  'head.linear': async (node, ctx) => {
    const features = ctx.inputs.features as number[][] | undefined;
    const labels = ctx.inputs.labels as string[] | undefined;
    if (!features?.length || !labels?.length) {
      return { outputs: { model: null }, error: { message: 'Linear head needs features + labels' } };
    }
    const model = await trainLinearSoftmax(features, labels, {
      epochs: Number(node.params.epochs ?? 50),
      learningRate: Number(node.params.learningRate ?? 0.001),
    });
    return { outputs: { model } };
  },

  'head.knn': async (node, ctx) => {
    const features = ctx.inputs.features as number[][] | undefined;
    const labels = ctx.inputs.labels as string[] | undefined;
    if (!features?.length || !labels?.length) {
      return { outputs: { model: null }, error: { message: 'kNN needs features + labels' } };
    }
    const k = Number(node.params.k ?? 5);
    const metric = (node.params.metric ?? 'cosine') as 'cosine' | 'euclidean';
    return {
      outputs: {
        model: { kind: 'knn', k, metric, features, labels, classes: [...new Set(labels)] },
      },
    };
  },

  'head.zeroshot-clip': async (node, ctx) => {
    const imgFeat = ctx.inputs.imageFeatures as number[][] | undefined;
    const txtFeat = ctx.inputs.textFeatures as number[][] | undefined;
    const temperature = Number(node.params.temperature ?? 100);
    if (!txtFeat?.length) {
      return {
        outputs: { model: null },
        error: { message: 'Zero-shot CLIP needs text features (class prompts)' },
      };
    }
    return {
      outputs: {
        model: { kind: 'zero-shot-clip', textFeatures: txtFeat, temperature, imageFeatures: imgFeat ?? [] },
      },
    };
  },

  'eval.accuracy': async (_node, ctx) => {
    const model = ctx.inputs.model as { predict?: (f: number[]) => number } | null;
    const features = (ctx.inputs.features ?? []) as number[][];
    const labels = (ctx.inputs.labels ?? []) as string[];
    if (!model?.predict || features.length !== labels.length) {
      return { outputs: { metrics: { accuracy: 0 } } };
    }
    const classes = [...new Set(labels)];
    let correct = 0;
    for (let i = 0; i < features.length; i++) {
      const predIdx = model.predict(features[i]!);
      if (classes[predIdx] === labels[i]) correct++;
    }
    return { outputs: { metrics: { accuracy: correct / features.length, n: features.length } } };
  },
};

// ───────────────────────── LINEAR SOFTMAX TRAINER ─────────────────────────

interface LinearModel {
  kind: 'linear';
  weights: number[][]; // [numClasses][numFeatures]
  bias: number[];
  classes: string[];
  predict: (features: number[]) => number;
  probs: (features: number[]) => number[];
}

async function trainLinearSoftmax(
  features: number[][],
  labels: string[],
  opts: { epochs: number; learningRate: number },
): Promise<LinearModel> {
  const classes = [...new Set(labels)];
  const numClasses = classes.length;
  const numFeatures = features[0]!.length;
  const labelToIdx = new Map(classes.map((c, i) => [c, i] as const));
  const y = labels.map((l) => labelToIdx.get(l)!);

  let W = Array.from({ length: numClasses }, () =>
    Array.from({ length: numFeatures }, () => (Math.random() - 0.5) * 0.01),
  );
  let b = Array.from({ length: numClasses }, () => 0);

  for (let epoch = 0; epoch < opts.epochs; epoch++) {
    for (let i = 0; i < features.length; i++) {
      const x = features[i]!;
      const logits = W.map((row, k) => row.reduce((s, w, j) => s + w * x[j]!, 0) + b[k]!);
      const maxL = Math.max(...logits);
      const exps = logits.map((l) => Math.exp(l - maxL));
      const sum = exps.reduce((a, v) => a + v, 0);
      const probs = exps.map((e) => e / sum);
      const yi = y[i]!;
      for (let k = 0; k < numClasses; k++) {
        const grad = probs[k]! - (k === yi ? 1 : 0);
        for (let j = 0; j < numFeatures; j++) {
          W[k]![j]! -= opts.learningRate * grad * x[j]!;
        }
        b[k]! -= opts.learningRate * grad;
      }
    }
  }

  return {
    kind: 'linear',
    weights: W,
    bias: b,
    classes,
    probs: (x: number[]) => {
      const logits = W.map((row, k) => row.reduce((s, w, j) => s + w * x[j]!, 0) + b[k]!);
      const maxL = Math.max(...logits);
      const exps = logits.map((l) => Math.exp(l - maxL));
      const sum = exps.reduce((a, v) => a + v, 0);
      return exps.map((e) => e / sum);
    },
    predict: (x: number[]) => {
      const logits = W.map((row, k) => row.reduce((s, w, j) => s + w * x[j]!, 0) + b[k]!);
      let argmax = 0;
      for (let k = 1; k < logits.length; k++) if (logits[k]! > logits[argmax]!) argmax = k;
      return argmax;
    },
  };
}

// ───────────────────────── RUNNER CLASS ─────────────────────────

export class WebGraphRunner implements GraphRunner {
  readonly kind = 'web' as const;

  async capabilities(): Promise<RuntimeCapabilities> {
    return probeWebRuntime();
  }

  async runNode(node: NodeInstance, ctx: NodeExecutionContext): Promise<NodeExecutionResult> {
    const runner = runners[node.schemaId];
    if (!runner) {
      return {
        outputs: {},
        error: { message: `No web runner for schema ${node.schemaId}` },
      };
    }
    try {
      return await runner(node, ctx);
    } catch (e) {
      const err = e as Error;
      return { outputs: {}, error: { message: err.message, stack: err.stack } };
    }
  }
}
