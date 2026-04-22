import { create } from 'zustand';
import type { RuntimeCapabilities } from '@wireml/nodes';

interface RuntimeState {
  kind: 'web' | 'local';
  local: RuntimeCapabilities | null;
  web: RuntimeCapabilities | null;
  probing: boolean;
  setLocal: (caps: RuntimeCapabilities | null) => void;
  setWeb: (caps: RuntimeCapabilities) => void;
  setProbing: (probing: boolean) => void;
  setKind: (kind: 'web' | 'local') => void;
}

export const useRuntimeStore = create<RuntimeState>((set) => ({
  kind: 'web',
  local: null,
  web: null,
  probing: true,
  setLocal: (local) => set({ local }),
  setWeb: (web) => set({ web }),
  setProbing: (probing) => set({ probing }),
  setKind: (kind) => set({ kind }),
}));

/** Probe the local runtime once at app load. Non-blocking. */
export async function probeLocalRuntime(): Promise<RuntimeCapabilities | null> {
  try {
    const res = await fetch('/runtime/capabilities', {
      method: 'GET',
      signal: AbortSignal.timeout(1500),
    });
    if (!res.ok) return null;
    return (await res.json()) as RuntimeCapabilities;
  } catch {
    return null;
  }
}

/** Probe browser-side capabilities (WebGPU presence, etc.). */
export async function probeWebRuntime(): Promise<RuntimeCapabilities> {
  const hasWebGPU = 'gpu' in navigator;
  let adapterName = 'webgpu (unknown)';
  let compute = 'unknown';
  if (hasWebGPU) {
    try {
      const adapter = await (navigator as any).gpu.requestAdapter();
      if (adapter) {
        const info = (adapter.info as { vendor?: string; architecture?: string; device?: string }) ?? {};
        adapterName = [info.vendor, info.architecture, info.device].filter(Boolean).join(' ') || 'WebGPU adapter';
        compute = `max buffer ${adapter.limits.maxStorageBufferBindingSize ?? 'n/a'}`;
      }
    } catch {
      /* ignore */
    }
  }
  return {
    kind: 'web',
    device: {
      type: 'webgpu',
      name: adapterName,
      compute,
    },
    supportedNodes: [],
    version: '0.1.0',
  };
}
