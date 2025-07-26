'use client';
import React, { useCallback, useState, useMemo, useEffect } from 'react';
import { apiFetch } from '@/utils/api';
import { useAuthStore } from '@/store/useAuthStore';
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
  book_id?: number;
  external_id?: string;
  status?: string;
  description?: string;
  is_recommendation?: boolean;
  reasoning?: string;
}

interface GraphData {
  nodes: Node<BookData>[];
  edges: Edge[];
  message: string;
}


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
  const isRecommendation = data.is_recommendation;
  
  return (
    <div className={`px-3 py-2 shadow-lg rounded-lg transition-colors cursor-pointer ${
      isRecommendation 
        ? 'bg-[#4a0e4e] border-2 border-[#e879f9] hover:border-[#f8bbff]' 
        : 'bg-[#001f3f] border-2 border-[#00aaff] hover:border-[#fa8537]'
    }`}>
      <div className={`font-semibold text-sm mb-1 ${
        isRecommendation ? 'text-[#f8bbff]' : 'text-[#e0f0ff]'
      }`}>
        {data.label}
        {isRecommendation && <span className="ml-1 text-xs">✨</span>}
      </div>
      {data.author && (
        <div className={`text-xs mb-1 ${
          isRecommendation ? 'text-[#e0c7f0]' : 'text-[#cceeff]'
        }`}>
          by {data.author}
        </div>
      )}
      {data.rating && (
        <div className="text-xs text-[#FFCE00] flex items-center">
          ⭐ {data.rating}
        </div>
      )}
      {data.status && (
        <div className={`text-xs mt-1 px-2 py-1 rounded text-center ${
          data.status === 'READ' ? 'bg-green-600 text-white' :
          data.status === 'reading' ? 'bg-blue-600 text-white' :
          'bg-gray-600 text-white'
        }`}>
          {data.status.replace('_', ' ').toUpperCase()}
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
  const user = useAuthStore((state) => state.user);
  const [nodes, setNodes] = useState<Node<BookData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node<BookData> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  console.log('🔧 BookRecommendationGraph component mounted, user:', user);
  
  // Fetch graph data from API
  useEffect(() => {
    console.log('🔄 useEffect triggered, user?.id:', user?.id);
    
    const fetchGraphData = async () => {
      if (!user?.id) {
        console.log('❌ No user ID found, user:', user);
        setLoading(false);
        return;
      }
      
      setLoading(true);
      setError(null);
      
      try {
        console.log('🔄 Fetching graph data for user:', user?.id);
        const graphData = await apiFetch<GraphData>('/recommendations/graph', {
          noCache: true
        });
        
        console.log('📊 API Response:', graphData);
        
        if (graphData && graphData.nodes && graphData.nodes.length > 0) {
          console.log('✅ Graph data received:', graphData);
          console.log('📚 Nodes:', graphData.nodes.length);
          console.log('🔗 Edges:', graphData.edges?.length || 0);
          console.log('Sample node:', graphData.nodes[0]);
          console.log('Sample edge:', graphData.edges?.[0]);
          
          setNodes(graphData.nodes);
          setEdges(graphData.edges || []);
        } else if (graphData && graphData.nodes && graphData.nodes.length === 0) {
          console.log('📝 No user books found');
          setError('No books found in your library. Add some books and reviews to generate your personal recommendation graph!');
        } else {
          console.log('❌ Invalid graph data received:', graphData);
          setError('No graph data available - please add books and reviews to your library');
        }
      } catch (err) {
        console.error('❌ Error fetching graph data:', err);
        setError('Failed to load recommendation graph. Please make sure you\'re logged in and have books in your library.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraphData();
  }, [user]);

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

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node as Node<BookData>);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Show loading state
  if (loading) {
    return (
      <div className="w-full">
        <div style={containerStyle} className="relative flex items-center justify-center">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-300 text-lg">Loading recommendation graph...</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Show error state
  if (error) {
    return (
      <div className="w-full">
        <div style={containerStyle} className="relative flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">📚</div>
            <h3 className="text-xl font-semibold text-gray-300 mb-2">Unable to load graph</h3>
            <p className="text-gray-400">{error}</p>
            <p className="text-gray-500 text-sm mt-2">Try reviewing some books first to generate recommendations!</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Show empty state
  if (nodes.length === 0 && !loading) {
    return (
      <div className="w-full">
        <div style={containerStyle} className="relative flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">📖</div>
            <h3 className="text-xl font-semibold text-gray-300 mb-2">No books to display</h3>
            <p className="text-gray-400">Add some books to your library and write reviews to see your recommendation graph!</p>
          </div>
        </div>
      </div>
    );
  }

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
                {selectedNode.data.status && (
                  <p className="text-xs sm:text-sm text-[#cceeff]">
                    <span className="font-medium text-[#00aaff]">Status:</span> {selectedNode.data.status.replace('_', ' ')}
                  </p>
                )}
                {selectedNode.data.is_recommendation && (
                  <div className="bg-purple-800 rounded-lg p-3 border-l-4 border-purple-400">
                    <p className="text-xs text-purple-200 mb-2">✨ AI Recommendation</p>
                    {selectedNode.data.reasoning && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-purple-300 mb-1">Why recommended:</p>
                        <p className="text-xs text-purple-100 leading-relaxed">
                          {selectedNode.data.reasoning}
                        </p>
                      </div>
                    )}
                  </div>
                )}
                {selectedNode.data.description && (
                  <div className="mt-2">
                    <p className="text-xs text-[#cceeff] max-h-20 overflow-y-auto">
                      {selectedNode.data.description}
                    </p>
                  </div>
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