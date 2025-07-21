'use client';
import React, { useCallback, useState, useMemo } from 'react';
import { 
  ReactFlow, 
  applyNodeChanges, 
  applyEdgeChanges, 
  addEdge, 
  Node, 
  Edge, 
  Connection, 
  NodeChange, 
  EdgeChange,
  Controls,
  Background,
  Panel,
  BackgroundVariant
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface BookData extends Record<string, unknown> {
  label: string;
  author?: string;
  rating?: number;
  genre?: string;
}

// Enhanced mock data with project color scheme
const initialNodes: Node<BookData>[] = [
  { 
    id: 'book-1', 
    position: { x: 100, y: 50 }, 
    data: { 
      label: 'The Hobbit', 
      author: 'J.R.R. Tolkien',
      rating: 4.5,
      genre: 'Fantasy'
    },
    style: {
      background: '#001f3f',
      border: '2px solid #00aaff',
      borderRadius: '8px',
      padding: '12px',
      minWidth: '160px',
      color: '#e0f0ff'
    }
  },
  { 
    id: 'book-2', 
    position: { x: 400, y: 50 }, 
    data: { 
      label: 'Lord of the Rings', 
      author: 'J.R.R. Tolkien',
      rating: 4.8,
      genre: 'Fantasy'
    },
    style: {
      background: '#0F52BA',
      border: '2px solid #fa8537',
      borderRadius: '8px',
      padding: '12px',
      minWidth: '160px',
      color: '#e0f0ff'
    }
  },
  { 
    id: 'book-3', 
    position: { x: 250, y: 200 }, 
    data: { 
      label: 'The Silmarillion', 
      author: 'J.R.R. Tolkien',
      rating: 4.2,
      genre: 'Fantasy'
    },
    style: {
      background: '#0a1f44',
      border: '2px solid #3F8EF3',
      borderRadius: '8px',
      padding: '12px',
      minWidth: '160px',
      color: '#cceeff'
    }
  },
  { 
    id: 'book-4', 
    position: { x: 550, y: 200 }, 
    data: { 
      label: 'Dune', 
      author: 'Frank Herbert',
      rating: 4.6,
      genre: 'Sci-Fi'
    },
    style: {
      background: '#001f3f',
      border: '2px solid #fc9957',
      borderRadius: '8px',
      padding: '12px',
      minWidth: '160px',
      color: '#e0f0ff'
    }
  },
  { 
    id: 'book-5', 
    position: { x: 50, y: 350 }, 
    data: { 
      label: 'Foundation', 
      author: 'Isaac Asimov',
      rating: 4.4,
      genre: 'Sci-Fi'
    },
    style: {
      background: '#0F52BA',
      border: '2px solid #60a5fa',
      borderRadius: '8px',
      padding: '12px',
      minWidth: '160px',
      color: '#e0f0ff'
    }
  },
  { 
    id: 'book-6', 
    position: { x: 350, y: 350 }, 
    data: { 
      label: 'Hyperion', 
      author: 'Dan Simmons',
      rating: 4.3,
      genre: 'Sci-Fi'
    },
    style: {
      background: '#0a1f44',
      border: '2px solid #00aaff',
      borderRadius: '8px',
      padding: '12px',
      minWidth: '160px',
      color: '#cceeff'
    }
  }
];

const initialEdges: Edge[] = [
  { 
    id: 'edge-1-2', 
    source: 'book-1', 
    target: 'book-2', 
    label: 'Same Author',
    style: { stroke: '#00aaff', strokeWidth: 3 },
    labelStyle: { 
      fill: '#ffffff', 
      fontWeight: 700, 
      fontSize: '13px',
      background: 'rgba(0, 170, 255, 0.8)',
      padding: '2px 4px',
      borderRadius: '4px'
    },
    labelBgStyle: { fill: 'rgba(0, 170, 255, 0.8)', fillOpacity: 0.9 }
  },
  { 
    id: 'edge-2-3', 
    source: 'book-2', 
    target: 'book-3', 
    label: 'Same Universe',
    style: { stroke: '#fa8537', strokeWidth: 3 },
    labelStyle: { 
      fill: '#ffffff', 
      fontWeight: 700, 
      fontSize: '13px',
      background: 'rgba(250, 133, 55, 0.9)',
      padding: '2px 4px',
      borderRadius: '4px'
    },
    labelBgStyle: { fill: 'rgba(250, 133, 55, 0.9)', fillOpacity: 0.9 }
  },
  { 
    id: 'edge-1-3', 
    source: 'book-1', 
    target: 'book-3', 
    label: 'Similar Style',
    style: { stroke: '#3F8EF3', strokeWidth: 2 },
    labelStyle: { 
      fill: '#ffffff', 
      fontWeight: 700, 
      fontSize: '13px',
      background: 'rgba(63, 142, 243, 0.9)',
      padding: '2px 4px',
      borderRadius: '4px'
    },
    labelBgStyle: { fill: 'rgba(63, 142, 243, 0.9)', fillOpacity: 0.9 }
  },
  { 
    id: 'edge-4-5', 
    source: 'book-4', 
    target: 'book-5', 
    label: 'Same Genre',
    style: { stroke: '#fc9957', strokeWidth: 3 },
    labelStyle: { 
      fill: '#ffffff', 
      fontWeight: 700, 
      fontSize: '13px',
      background: 'rgba(252, 153, 87, 0.9)',
      padding: '2px 4px',
      borderRadius: '4px'
    },
    labelBgStyle: { fill: 'rgba(252, 153, 87, 0.9)', fillOpacity: 0.9 }
  },
  { 
    id: 'edge-5-6', 
    source: 'book-5', 
    target: 'book-6', 
    label: 'Space Opera',
    style: { stroke: '#60a5fa', strokeWidth: 2 },
    labelStyle: { 
      fill: '#ffffff', 
      fontWeight: 700, 
      fontSize: '13px',
      background: 'rgba(96, 165, 250, 0.9)',
      padding: '2px 4px',
      borderRadius: '4px'
    },
    labelBgStyle: { fill: 'rgba(96, 165, 250, 0.9)', fillOpacity: 0.9 }
  },
  { 
    id: 'edge-4-6', 
    source: 'book-4', 
    target: 'book-6', 
    label: 'Complex Narratives',
    style: { stroke: '#00aaff', strokeWidth: 2 },
    labelStyle: { 
      fill: '#ffffff', 
      fontWeight: 700, 
      fontSize: '13px',
      background: 'rgba(0, 170, 255, 0.9)',
      padding: '2px 4px',
      borderRadius: '4px'
    },
    labelBgStyle: { fill: 'rgba(0, 170, 255, 0.9)', fillOpacity: 0.9 }
  }
];

const containerStyle: React.CSSProperties = {
  width: '100%',
  height: '70vh',
  minHeight: 400,
  background: '#0a1128',
  borderRadius: 12,
  boxShadow: '0 4px 12px rgba(0,170,255,0.2)',
  border: '1px solid #3F8EF3',
  overflow: 'hidden'
};

// Custom node component
const CustomBookNode = ({ data }: { data: BookData }) => {
  return (
    <div className="px-3 py-2 shadow-lg rounded-lg bg-[#001f3f] border-2 border-[#00aaff] hover:border-[#fa8537] transition-colors cursor-pointer">
      <div className="font-semibold text-sm text-[#e0f0ff] mb-1">{data.label}</div>
      {data.author && <div className="text-xs text-[#cceeff] mb-1">by {data.author}</div>}
      {data.rating && (
        <div className="text-xs text-[#FFCE00] flex items-center">
          ⭐ {data.rating}
        </div>
      )}
    </div>
  );
};

const nodeTypes = {
  bookNode: CustomBookNode,
};

// Utility to ensure unique ids for nodes/edges
function uniqueById<T extends { id: string }>(arr: T[]): T[] {
  const seen = new Set();
  return arr.filter(item => {
    if (seen.has(item.id)) return false;
    seen.add(item.id);
    return true;
  });
}

const BookRecommendationGraph: React.FC = () => {
  const [nodes, setNodes] = useState<Node<BookData>[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node<BookData> | null>(null);

  // Deduplicate before rendering
  const uniqueNodes = useMemo(() => uniqueById(nodes), [nodes]);
  const uniqueEdges = useMemo(() => uniqueById(edges), [edges]);

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds) as Node<BookData>[]);
  }, []);

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
  }, []);

  const onConnect = useCallback((connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  }, []);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node as Node<BookData>);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  return (
    <div className="w-full">
      <div 
        style={containerStyle}
        className="relative"
      >
        <ReactFlow
          nodes={uniqueNodes as Node[]}
          edges={uniqueEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls 
            showInteractive={false} 
            className="!shadow-lg"
            style={{
              background: '#001f3f',
              border: '1px solid #00aaff'
            }}
          />
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#3F8EF3" />
          
          {selectedNode && (
            <Panel 
              position="top-left" 
              className="bg-[#001f3f] rounded-lg shadow-lg p-3 sm:p-4 border border-[#3F8EF3] max-w-xs sm:max-w-sm mx-2 sm:mx-0"
              style={{ boxShadow: '0 4px 12px rgba(0,170,255,0.3)' }}
            >
              <div className="space-y-2">
                <h3 className="font-bold text-base sm:text-lg text-[#e0f0ff] break-words">
                  {selectedNode.data.label}
                </h3>
                {selectedNode.data.author && (
                  <p className="text-xs sm:text-sm text-[#cceeff]">
                    <span className="font-medium text-[#00aaff]">Author:</span> {selectedNode.data.author}
                  </p>
                )}
                {selectedNode.data.genre && (
                  <p className="text-xs sm:text-sm text-[#cceeff]">
                    <span className="font-medium text-[#00aaff]">Genre:</span> {selectedNode.data.genre}
                  </p>
                )}
                {selectedNode.data.rating && (
                  <p className="text-xs sm:text-sm text-[#cceeff] flex items-center">
                    <span className="font-medium text-[#00aaff] mr-2">Rating:</span>
                    <span className="text-[#FFCE00]">⭐ {selectedNode.data.rating}</span>
                  </p>
                )}
                <button
                  onClick={() => setSelectedNode(null)}
                  className="mt-3 text-xs bg-[#fa8537] hover:bg-[#fc9957] text-white px-3 py-1 rounded transition-colors w-full sm:w-auto font-medium"
                >
                  Close
                </button>
              </div>
            </Panel>
          )}
        </ReactFlow>
      </div>
      
      <div className="mt-4 text-xs sm:text-sm text-[#cceeff] bg-[#0a1f44] border border-[#3F8EF3] p-3 rounded-lg">
        <p className="font-medium mb-2 text-[#e0f0ff]">How to use:</p>
        <ul className="space-y-1 text-xs">
          <li>• Click and drag to pan around the graph</li>
          <li>• Use mouse wheel or controls to zoom in/out</li>
          <li>• Click on any book node to view details</li>
          <li>• Edges show recommendation relationships between books</li>
        </ul>
      </div>
    </div>
  );
};

export default BookRecommendationGraph; 