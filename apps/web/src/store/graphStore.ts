import { create } from 'zustand';
import type { GraphJSON, NodeInstance, Edge } from '@wireml/nodes';
import { nanoid } from '../lib/nanoid';

interface GraphState {
  graph: GraphJSON;
  selectedNodeId: string | null;
  dirty: boolean;

  setGraph: (graph: GraphJSON) => void;
  addNode: (schemaId: string, position: { x: number; y: number }) => string;
  removeNode: (nodeId: string) => void;
  updateNodeParams: (nodeId: string, params: Record<string, unknown>) => void;
  moveNode: (nodeId: string, position: { x: number; y: number }) => void;
  addEdge: (edge: Omit<Edge, 'id'>) => void;
  removeEdge: (edgeId: string) => void;
  select: (nodeId: string | null) => void;
  clear: () => void;
}

const emptyGraph: GraphJSON = {
  version: 1,
  name: 'Untitled graph',
  nodes: [],
  edges: [],
  meta: {},
};

export const useGraphStore = create<GraphState>((set) => ({
  graph: emptyGraph,
  selectedNodeId: null,
  dirty: false,

  setGraph: (graph) => set({ graph, selectedNodeId: null, dirty: false }),

  addNode: (schemaId, position) => {
    const id = `n_${nanoid(8)}`;
    const instance: NodeInstance = { id, schemaId, position, params: {} };
    set((s) => ({
      graph: { ...s.graph, nodes: [...s.graph.nodes, instance] },
      selectedNodeId: id,
      dirty: true,
    }));
    return id;
  },

  removeNode: (nodeId) =>
    set((s) => ({
      graph: {
        ...s.graph,
        nodes: s.graph.nodes.filter((n) => n.id !== nodeId),
        edges: s.graph.edges.filter(
          (e) => e.source.nodeId !== nodeId && e.target.nodeId !== nodeId,
        ),
      },
      selectedNodeId: s.selectedNodeId === nodeId ? null : s.selectedNodeId,
      dirty: true,
    })),

  updateNodeParams: (nodeId, params) =>
    set((s) => ({
      graph: {
        ...s.graph,
        nodes: s.graph.nodes.map((n) =>
          n.id === nodeId ? { ...n, params: { ...n.params, ...params } } : n,
        ),
      },
      dirty: true,
    })),

  moveNode: (nodeId, position) =>
    set((s) => ({
      graph: {
        ...s.graph,
        nodes: s.graph.nodes.map((n) => (n.id === nodeId ? { ...n, position } : n)),
      },
      dirty: true,
    })),

  addEdge: (edge) => {
    const full: Edge = { ...edge, id: `e_${nanoid(8)}` };
    set((s) => ({
      graph: { ...s.graph, edges: [...s.graph.edges, full] },
      dirty: true,
    }));
  },

  removeEdge: (edgeId) =>
    set((s) => ({
      graph: { ...s.graph, edges: s.graph.edges.filter((e) => e.id !== edgeId) },
      dirty: true,
    })),

  select: (nodeId) => set({ selectedNodeId: nodeId }),

  clear: () => set({ graph: emptyGraph, selectedNodeId: null, dirty: false }),
}));
