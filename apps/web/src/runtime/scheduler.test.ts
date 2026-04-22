import { describe, it, expect } from 'vitest';
import { topoSort } from '@wireml/nodes';
import type { GraphJSON } from '@wireml/nodes';

describe('topoSort', () => {
  const make = (nodes: string[], edges: [string, string][]): GraphJSON => ({
    version: 1,
    name: 't',
    nodes: nodes.map((id) => ({ id, schemaId: 'data.webcam', position: { x: 0, y: 0 }, params: {} })),
    edges: edges.map(([s, t], i) => ({
      id: `e${i}`,
      source: { nodeId: s, port: 'frames' },
      target: { nodeId: t, port: 'images' },
    })),
  });

  it('orders a simple chain', () => {
    const g = make(['a', 'b', 'c'], [
      ['a', 'b'],
      ['b', 'c'],
    ]);
    const order = topoSort(g).map((n) => n.id);
    expect(order).toEqual(['a', 'b', 'c']);
  });

  it('orders a diamond', () => {
    const g = make(['a', 'b', 'c', 'd'], [
      ['a', 'b'],
      ['a', 'c'],
      ['b', 'd'],
      ['c', 'd'],
    ]);
    const order = topoSort(g).map((n) => n.id);
    expect(order[0]).toBe('a');
    expect(order[3]).toBe('d');
    expect(order.slice(1, 3).sort()).toEqual(['b', 'c']);
  });

  it('throws on cycles', () => {
    const g = make(['a', 'b'], [
      ['a', 'b'],
      ['b', 'a'],
    ]);
    expect(() => topoSort(g)).toThrow(/cycle/i);
  });
});
