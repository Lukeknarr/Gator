'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { motion } from 'framer-motion';

interface Interest {
  id: number;
  topic: string;
  weight: number;
  source: string;
  created_at: string;
}

interface InterestGraphProps {
  interests: Interest[];
  isLoading: boolean;
}

export function InterestGraph({ interests, isLoading }: InterestGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<any>(null);

  useEffect(() => {
    if (!interests.length || !svgRef.current) return;

    // Create graph data
    const nodes = interests.map(interest => ({
      id: interest.id,
      label: interest.topic,
      weight: interest.weight,
      source: interest.source,
    }));

    // Create edges between related interests
    const edges: any[] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const node1 = nodes[i];
        const node2 = nodes[j];
        
        // Simple similarity check
        const words1 = node1.label.toLowerCase().split(' ');
        const words2 = node2.label.toLowerCase().split(' ');
        const commonWords = words1.filter(word => words2.includes(word));
        
        if (commonWords.length > 0) {
          edges.push({
            source: node1.id,
            target: node2.id,
            weight: commonWords.length / Math.max(words1.length, words2.length),
          });
        }
      }
    }

    setGraphData({ nodes, edges });
  }, [interests]);

  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;

    // Create force simulation
    const simulation = d3.forceSimulation(graphData.nodes)
      .force('link', d3.forceLink(graphData.edges).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Create links
    const links = svg.append('g')
      .selectAll('line')
      .data(graphData.edges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.weight) * 3);

    // Create nodes
    const nodes = svg.append('g')
      .selectAll('g')
      .data(graphData.nodes)
      .enter()
      .append('g')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add circles to nodes
    nodes.append('circle')
      .attr('r', (d: any) => Math.sqrt(d.weight) * 8 + 5)
      .attr('fill', (d: any) => {
        switch (d.source) {
          case 'onboarding': return '#3b82f6';
          case 'manual': return '#10b981';
          case 'passive': return '#f59e0b';
          default: return '#6b7280';
        }
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels to nodes
    nodes.append('text')
      .text((d: any) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('font-size', '12px')
      .attr('fill', '#374151')
      .attr('font-weight', '500');

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodes
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [graphData]);

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (!interests.length) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            No interests yet
          </h3>
          <p className="text-secondary-600 mb-4">
            Add some interests to see your knowledge graph
          </p>
          <button className="btn-primary">Add Interest</button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="card"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-secondary-900 mb-2">
          Your Interest Graph
        </h3>
        <p className="text-sm text-secondary-600">
          Visualize how your interests connect and evolve
        </p>
      </div>
      
      <div className="overflow-hidden rounded-lg border border-secondary-200">
        <svg
          ref={svgRef}
          width="100%"
          height="600"
          viewBox="0 0 800 600"
          className="w-full h-auto"
        />
      </div>
      
      <div className="mt-4 flex flex-wrap gap-4 text-sm text-secondary-600">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
          <span>Onboarding</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
          <span>Manual</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
          <span>Passive</span>
        </div>
      </div>
    </motion.div>
  );
} 