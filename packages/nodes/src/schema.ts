/**
 * Shared node schema types. This contract is honored by both the browser
 * runtime (Transformers.js / ONNX Runtime Web) and the local Python runtime
 * (FastAPI + PyTorch / MLX). A graph authored in one runtime must load and
 * run in the other.
 */

export type Category =
  | 'data'
  | 'preprocess'
  | 'backbone'
  | 'head'
  | 'eval'
  | 'deploy';

export type PortType =
  | 'image'
  | 'audio'
  | 'text'
  | 'tensor'
  | 'features'
  | 'labels'
  | 'model'
  | 'metrics'
  | 'any';

export type ExecutionMode = 'reactive' | 'triggered';

export interface Port {
  name: string;
  type: PortType;
  optional?: boolean;
  array?: boolean;
}

export interface ParamSpec {
  name: string;
  label?: string;
  kind: 'string' | 'number' | 'enum' | 'boolean' | 'file' | 'json';
  default?: unknown;
  options?: readonly string[];
  min?: number;
  max?: number;
  step?: number;
  description?: string;
}

export interface Capability {
  /** Can run in a browser WebGPU context. */
  web?: boolean;
  /** Minimum VRAM in GB to recommend for local-mode execution. */
  minVramGb?: number;
  /** Requires native Python runtime (cannot run in the browser). */
  localOnly?: boolean;
  /** Approximate model download size in MB. */
  downloadMb?: number;
}

export interface NodeSchema {
  /** Stable identifier, e.g. "data.webcam", "backbone.clip.vit-b-32". */
  id: string;
  /** Human-readable display name. */
  name: string;
  category: Category;
  /** One-line summary shown in node library and inspector. */
  description: string;
  inputs: readonly Port[];
  outputs: readonly Port[];
  params: readonly ParamSpec[];
  capability: Capability;
  executionMode: ExecutionMode;
  /** Optional icon name (lucide-react). */
  icon?: string;
}

export interface NodeInstance {
  id: string;
  schemaId: string;
  position: { x: number; y: number };
  params: Record<string, unknown>;
}

export interface Edge {
  id: string;
  source: { nodeId: string; port: string };
  target: { nodeId: string; port: string };
}

export interface GraphJSON {
  /** Schema version of the graph file format. */
  version: 1;
  name: string;
  description?: string;
  nodes: NodeInstance[];
  edges: Edge[];
  /** Template-level metadata. */
  meta?: {
    author?: string;
    createdAt?: string;
    updatedAt?: string;
    tags?: string[];
  };
}

/** Runtime capabilities reported by a LocalGraphRunner's /capabilities endpoint. */
export interface RuntimeCapabilities {
  kind: 'web' | 'local';
  device: {
    type: 'cuda' | 'mps' | 'mlx' | 'rocm' | 'directml' | 'xpu' | 'cpu' | 'webgpu';
    name: string;
    vramGb?: number;
    compute?: string;
  };
  /** IDs of nodes this runtime can execute. */
  supportedNodes: string[];
  version: string;
}
