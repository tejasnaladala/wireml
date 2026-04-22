import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Connection,
  type Node,
  type Edge as RFEdge,
  type NodeChange,
  type EdgeChange,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useGraphStore } from '@/store/graphStore';
import { NodeView } from './NodeView';

const nodeTypes = { wireml: NodeView };

export function Canvas() {
  const graph = useGraphStore((s) => s.graph);
  const addEdge = useGraphStore((s) => s.addEdge);
  const removeEdge = useGraphStore((s) => s.removeEdge);
  const removeNode = useGraphStore((s) => s.removeNode);
  const moveNode = useGraphStore((s) => s.moveNode);
  const select = useGraphStore((s) => s.select);

  const rfNodes: Node[] = useMemo(
    () =>
      graph.nodes.map((n) => ({
        id: n.id,
        type: 'wireml',
        position: n.position,
        data: { schemaId: n.schemaId },
      })),
    [graph.nodes],
  );

  const rfEdges: RFEdge[] = useMemo(
    () =>
      graph.edges.map((e) => ({
        id: e.id,
        source: e.source.nodeId,
        sourceHandle: e.source.port,
        target: e.target.nodeId,
        targetHandle: e.target.port,
      })),
    [graph.edges],
  );

  const onConnect = useCallback(
    (conn: Connection) => {
      if (!conn.source || !conn.target || !conn.sourceHandle || !conn.targetHandle) return;
      addEdge({
        source: { nodeId: conn.source, port: conn.sourceHandle },
        target: { nodeId: conn.target, port: conn.targetHandle },
      });
    },
    [addEdge],
  );

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const next = applyNodeChanges(changes, rfNodes);
      // Reflect position changes + deletions into the store.
      for (const ch of changes) {
        if (ch.type === 'position' && ch.position) {
          moveNode(ch.id, ch.position);
        } else if (ch.type === 'remove') {
          removeNode(ch.id);
        } else if (ch.type === 'select' && ch.selected) {
          select(ch.id);
        }
      }
      return next;
    },
    [rfNodes, moveNode, removeNode, select],
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      for (const ch of changes) {
        if (ch.type === 'remove') removeEdge(ch.id);
      }
      return applyEdgeChanges(changes, rfEdges);
    },
    [rfEdges, removeEdge],
  );

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        defaultEdgeOptions={{ type: 'smoothstep', animated: false }}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        snapToGrid
        snapGrid={[16, 16]}
        colorMode="dark"
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={24} size={1} color="#1a222d" />
        <Controls showInteractive={false} />
        <MiniMap
          pannable
          zoomable
          nodeColor={() => '#3b82f6'}
          maskColor="rgba(10, 14, 20, 0.7)"
          style={{ background: '#131921', border: '1px solid #2a3240' }}
        />
      </ReactFlow>
    </div>
  );
}
