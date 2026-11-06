import React, { useCallback, useState } from 'react';
import ReactFlow, { 
  Background, Controls, MiniMap, useNodesState, useEdgesState,
  Handle, Position
} from 'reactflow';
import 'reactflow/dist/style.css';

// Custom Document Node
function DocumentNode({ data }) {
  const [showInfo, setShowInfo] = useState(false);
  
  return (
    <div 
      className="relative"
      onMouseEnter={() => setShowInfo(true)}
      onMouseLeave={() => setShowInfo(false)}
    >
      <Handle type="target" position={Position.Left} style={{ background: '#45D6E8' }} />
      
      <div style={{
        background: 'linear-gradient(135deg, rgba(16,28,43,0.95) 0%, rgba(26,45,66,0.95) 100%)',
        border: '1px solid rgba(69,214,232,0.4)',
        borderRadius: 12,
        padding: '12px 16px',
        minWidth: 180,
        boxShadow: '0 8px 32px rgba(0,0,0,0.5), 0 0 20px rgba(69,214,232,0.1)',
        backdropFilter: 'blur(10px)',
      }}>
        <div style={{ color: '#45D6E8', fontWeight: 700, fontSize: 12, marginBottom: 4 }}>
          📄 {data.documentType || 'Document'}
        </div>
        <div style={{ color: '#fff', fontWeight: 600, fontSize: 11, wordBreak: 'break-word' }}>
          {data.label?.length > 25 ? data.label.slice(0, 25) + '…' : data.label}
        </div>
        <div style={{ color: '#64748B', fontSize: 9, fontFamily: 'monospace', marginTop: 4 }}>
          {data.documentId}
        </div>
        
        {/* Key fields preview */}
        {data.fields && Object.keys(data.fields).length > 0 && (
          <div style={{ marginTop: 8, borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 6 }}>
            {Object.entries(data.fields).slice(0, 3).map(([k, v]) => (
              <div key={k} style={{ display: 'flex', gap: 4, fontSize: 9 }}>
                <span style={{ color: '#64748B' }}>{k.replace(/_/g, ' ')}:</span>
                <span style={{ color: '#94A3B8' }}>{String(v).slice(0, 20)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} style={{ background: '#45D6E8' }} />
    </div>
  );
}

// Custom edge label
function ConflictEdgeLabel({ data }) {
  return (
    <div style={{
      background: 'rgba(239,68,68,0.9)',
      border: '1px solid rgba(239,68,68,0.5)',
      borderRadius: 6,
      padding: '2px 6px',
      fontSize: 9,
      color: '#fff',
      fontWeight: 600,
    }}>
      ⚠ {data?.fieldName}
    </div>
  );
}

const nodeTypes = { documentNode: DocumentNode };

export default function RelationshipGraph({ nodes: initialNodes, edges: initialEdges }) {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);
  const [selectedElement, setSelectedElement] = useState(null);

  const onNodeClick = useCallback((_, node) => {
    setSelectedElement({ type: 'node', data: node.data });
  }, []);

  const onEdgeClick = useCallback((_, edge) => {
    setSelectedElement({ type: 'edge', data: edge.data });
  }, []);

  if (!initialNodes?.length) {
    return (
      <div style={{ height: '100%' }} className="flex items-center justify-center text-slate-500">
        No documents to display in the graph
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        style={{ background: 'transparent' }}
      >
        <Background 
          color="rgba(69,214,232,0.05)" 
          gap={40} 
          style={{ background: 'rgba(16,28,43,0.5)' }} 
        />
        <Controls style={{ background: 'rgba(16,28,43,0.9)', border: '1px solid rgba(255,255,255,0.1)' }} />
        <MiniMap 
          style={{ background: 'rgba(16,28,43,0.9)', border: '1px solid rgba(255,255,255,0.1)' }}
          nodeColor={() => '#45D6E8'}
        />
      </ReactFlow>

      {/* Info Panel */}
      {selectedElement && (
        <div style={{
          position: 'absolute',
          top: 10,
          right: 10,
          background: 'rgba(16,28,43,0.95)',
          border: '1px solid rgba(69,214,232,0.3)',
          borderRadius: 10,
          padding: '12px 16px',
          maxWidth: 280,
          backdropFilter: 'blur(10px)',
          zIndex: 10,
        }}>
          <button
            onClick={() => setSelectedElement(null)}
            style={{ float: 'right', color: '#64748B', background: 'none', border: 'none', cursor: 'pointer', fontSize: 14 }}
          >×</button>

          {selectedElement.type === 'node' ? (
            <>
              <div style={{ color: '#45D6E8', fontWeight: 700, fontSize: 12, marginBottom: 8 }}>
                Document Details
              </div>
              <div style={{ color: '#fff', fontWeight: 600, fontSize: 11, marginBottom: 6 }}>
                {selectedElement.data.label}
              </div>
              {selectedElement.data.fields && Object.entries(selectedElement.data.fields).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', gap: 6, fontSize: 10, marginBottom: 3 }}>
                  <span style={{ color: '#64748B', minWidth: 100 }}>{k.replace(/_/g, ' ')}:</span>
                  <span style={{ color: '#CBD5E1' }}>{v}</span>
                </div>
              ))}
            </>
          ) : (
            <>
              <div style={{ color: '#EF4444', fontWeight: 700, fontSize: 12, marginBottom: 8 }}>
                ⚠ {selectedElement.data?.fieldName} Conflict
              </div>
              {selectedElement.data?.conflictingValues && Object.entries(selectedElement.data.conflictingValues).map(([k, v]) => (
                <div key={k} style={{ marginBottom: 4 }}>
                  <div style={{ color: '#64748B', fontSize: 9, fontFamily: 'monospace' }}>{k.slice(-8)}</div>
                  <div style={{ color: '#FCA5A5', fontSize: 11, fontWeight: 600 }}>"{v}"</div>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: 40,
        left: 10,
        background: 'rgba(16,28,43,0.9)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 8,
        padding: '8px 12px',
        display: 'flex',
        gap: 12,
        fontSize: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <div style={{ width: 20, height: 2, background: '#22C55E' }} />
          <span style={{ color: '#94A3B8' }}>Matching</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <div style={{ width: 20, height: 2, background: '#EF4444' }} />
          <span style={{ color: '#94A3B8' }}>Conflict</span>
        </div>
      </div>
    </div>
  );
}

