/**
 * Scheduler: walks the graph in topological order and runs each node on
 * the chosen runtime, threading outputs as inputs to downstream nodes.
 *
 * Reactive nodes re-execute when their upstreams emit; triggered nodes
 * execute only when the user clicks Run (or a downstream triggered node
 * requests their result).
 */

import {
  type GraphJSON,
  type GraphRunner,
  type NodeInstance,
  getSchema,
  topoSort,
} from '@wireml/nodes';

export interface NodeResultEntry {
  nodeId: string;
  status: 'pending' | 'running' | 'ok' | 'error';
  outputs?: Record<string, unknown>;
  error?: { message: string };
}

export async function* runGraph(
  graph: GraphJSON,
  runner: GraphRunner,
  signal?: AbortSignal,
): AsyncGenerator<NodeResultEntry> {
  const sorted = topoSort(graph);
  const state = new Map<string, Record<string, unknown>>();

  for (const node of sorted) {
    if (signal?.aborted) return;
    yield { nodeId: node.id, status: 'running' };
    const inputs = collectInputs(node, graph, state);
    const result = await runner.runNode(node, { inputs, graph, signal });
    if (result.error) {
      yield { nodeId: node.id, status: 'error', error: result.error };
      // Continue — downstream nodes may still run independently.
    } else {
      state.set(node.id, result.outputs);
      yield { nodeId: node.id, status: 'ok', outputs: result.outputs };
    }
  }
}

function collectInputs(
  node: NodeInstance,
  graph: GraphJSON,
  state: Map<string, Record<string, unknown>>,
): Record<string, unknown> {
  const inputs: Record<string, unknown> = {};
  const schema = getSchema(node.schemaId);
  for (const port of schema.inputs) {
    const edges = graph.edges.filter(
      (e) => e.target.nodeId === node.id && e.target.port === port.name,
    );
    if (edges.length === 0) continue;
    if (port.array) {
      // Concatenate all upstream outputs for this array input.
      const collected: unknown[] = [];
      for (const e of edges) {
        const upstream = state.get(e.source.nodeId);
        const val = upstream?.[e.source.port];
        if (Array.isArray(val)) collected.push(...val);
        else if (val !== undefined) collected.push(val);
      }
      inputs[port.name] = collected;
    } else {
      const e = edges[0]!;
      const upstream = state.get(e.source.nodeId);
      inputs[port.name] = upstream?.[e.source.port];
    }
  }
  return inputs;
}
