"use client";

import React, { useEffect, useState, useRef, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { api, getErrorMessage } from "@/lib/api";
import { riskLevelToColor } from "@/lib/utils";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  Share2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  AlertTriangle,
  Info,
  ExternalLink,
  Layers,
  ArrowRight,
  ShieldAlert,
  X,
} from "lucide-react";
import * as d3 from "d3";

interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  risk_level: string;
  risk_score: number;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  amount: number;
}

function GraphContent() {
  const searchParams = useSearchParams();
  const initialAccount = searchParams.get("account") || "ACC_1025";

  const [accountId, setAccountId] = useState(initialAccount);
  const [currentCenter, setCurrentCenter] = useState(initialAccount);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; edges: GraphLink[] } | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const containerRef = useRef<HTMLDivElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

  const fetchGraph = useCallback(async (id: string) => {
    if (!id) return;
    setLoading(true);
    setError("");
    setSelectedNode(null);
    try {
      const res = await api.get(`/graph/subgraph/${id}`);
      setGraphData({
        nodes: res.data.nodes || [],
        edges: res.data.edges || [],
      });
      setCurrentCenter(id);
    } catch (err) {
      setError(getErrorMessage(err));
      setGraphData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraph(initialAccount);
  }, [fetchGraph, initialAccount]);

  // Render D3 Simulation
  useEffect(() => {
    if (!graphData || !svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth || 900;
    const height = 560;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Defs for directional arrows
    const defs = svg.append("defs");
    defs
      .append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 22)
      .attr("refY", 0)
      .attr("markerWidth", 5)
      .attr("markerHeight", 5)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#71717a");

    const g = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);
    zoomBehaviorRef.current = zoom;

    const simulation = d3
      .forceSimulation<GraphNode>(graphData.nodes)
      .force(
        "link",
        d3
          .forceLink<GraphNode, GraphLink>(graphData.edges)
          .id((d) => d.id)
          .distance(110)
      )
      .force("charge", d3.forceManyBody().strength(-350))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(35));

    // Draw links
    const link = g
      .append("g")
      .attr("stroke", "#3f3f46")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(graphData.edges)
      .join("line")
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#arrow)");

    // Draw node groups
    const node = g
      .append("g")
      .selectAll("g")
      .data(graphData.nodes)
      .join("g")
      .attr("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
      })
      .call(
        d3
          .drag<SVGGElement, GraphNode>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Node outer halo for center node
    node
      .filter((d) => d.id === currentCenter)
      .append("circle")
      .attr("r", 24)
      .attr("fill", "none")
      .attr("stroke", "#3b82f6")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "3 3")
      .attr("opacity", 0.8);

    // Node core circle
    node
      .append("circle")
      .attr("r", (d) => (d.id === currentCenter ? 18 : 13))
      .attr("fill", (d) => riskLevelToColor(d.risk_level))
      .attr("stroke", "#18181b")
      .attr("stroke-width", 2.5)
      .attr("shadow", "0 0 10px rgba(0,0,0,0.5)");

    // Node label
    node
      .append("text")
      .text((d) => d.id)
      .attr("x", 16)
      .attr("y", 4)
      .attr("fill", "#e4e4e7")
      .attr("font-size", "11px")
      .attr("font-family", "ui-monospace, SFMono-Regular, monospace")
      .attr("font-weight", (d) => (d.id === currentCenter ? "600" : "400"));

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as GraphNode).x!)
        .attr("y1", (d) => (d.source as GraphNode).y!)
        .attr("x2", (d) => (d.target as GraphNode).x!)
        .attr("y2", (d) => (d.target as GraphNode).y!);

      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });
  }, [graphData, currentCenter]);

  // Zoom controls
  const handleZoom = (factor: number) => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current).transition().duration(250).call(zoomBehaviorRef.current.scaleBy, factor);
  };

  const handleResetZoom = () => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current)
      .transition()
      .duration(300)
      .call(zoomBehaviorRef.current.transform, d3.zoomIdentity);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Graph Network Correlation"
        description="Topological graph correlation mapping fund flows, fan-in/fan-out dispersal patterns, and coordinated mule rings."
      />

      {/* Search & Suggestions Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchGraph(accountId);
          }}
          className="flex items-center gap-2 max-w-md w-full"
        >
          <Input
            placeholder="Account ID (e.g. ACC_1025)"
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            icon={<Search className="w-3.5 h-3.5" />}
            className="h-9 text-xs"
          />
          <Button type="submit" size="sm" disabled={loading} className="h-9 text-xs shrink-0">
            {loading ? "Exploring..." : "Trace Subgraph"}
          </Button>
        </form>

        {/* Preset quick test accounts */}
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="text-[11px]">Presets:</span>
          {["ACC_1025", "ACC_1001", "ACC_1004"].map((preset) => (
            <button
              key={preset}
              type="button"
              onClick={() => {
                setAccountId(preset);
                fetchGraph(preset);
              }}
              className="px-2 py-1 rounded bg-muted/60 hover:bg-muted text-[11px] font-mono border border-border/50 text-foreground transition-colors"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3.5 bg-destructive/15 border border-destructive/30 rounded-lg text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => fetchGraph(accountId)} className="h-7 text-xs text-rose-300">
            Retry
          </Button>
        </div>
      )}

      {/* Main Canvas Card */}
      <Card ref={containerRef} className="relative overflow-hidden border-border/70 bg-card/40">
        {/* Canvas Floating Top Bar */}
        <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-background/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-border/60 text-xs shadow-sm">
          <Share2 className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-mono font-medium text-foreground">Focus: {currentCenter}</span>
          <span className="text-muted-foreground">•</span>
          <span className="text-muted-foreground">
            {graphData?.nodes.length || 0} Nodes, {graphData?.edges.length || 0} Links
          </span>
        </div>

        {/* Floating Controls (Zoom & Reset) */}
        <div className="absolute top-4 right-4 z-10 flex items-center gap-1 bg-background/80 backdrop-blur-md p-1 rounded-lg border border-border/60 shadow-sm">
          <button
            type="button"
            onClick={() => handleZoom(1.3)}
            title="Zoom In"
            className="p-1.5 text-muted-foreground hover:text-foreground rounded hover:bg-muted transition-colors"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => handleZoom(0.7)}
            title="Zoom Out"
            className="p-1.5 text-muted-foreground hover:text-foreground rounded hover:bg-muted transition-colors"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={handleResetZoom}
            title="Reset View"
            className="p-1.5 text-muted-foreground hover:text-foreground rounded hover:bg-muted transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        {/* Floating Risk Legend */}
        <div className="absolute bottom-4 left-4 z-10 hidden sm:flex items-center gap-3 bg-background/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-border/60 text-[11px] text-muted-foreground shadow-sm">
          <span className="font-medium text-foreground">Risk Tier:</span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500" /> Low
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-lime-500" /> Moderate
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500" /> Elevated
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-orange-500" /> High
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-rose-500" /> Critical
          </span>
        </div>

        {/* Interactive Node Inspector Card */}
        {selectedNode && (
          <div className="absolute bottom-4 right-4 z-20 w-72 bg-card/95 border border-border/80 rounded-lg p-4 shadow-xl backdrop-blur-md">
            <div className="flex items-center justify-between pb-2 border-b border-border/50">
              <span className="text-xs font-semibold text-foreground font-mono">
                {selectedNode.id}
              </span>
              <button
                type="button"
                onClick={() => setSelectedNode(null)}
                className="text-muted-foreground hover:text-foreground p-0.5 rounded"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Classification:</span>
                <RiskBadge level={selectedNode.risk_level} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Risk Score:</span>
                <span className="font-mono font-bold text-foreground">
                  {selectedNode.risk_score}
                </span>
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-border/40 flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs h-7"
                onClick={() => {
                  setAccountId(selectedNode.id);
                  fetchGraph(selectedNode.id);
                }}
              >
                Center on Node
              </Button>
            </div>
          </div>
        )}

        {/* SVG Canvas */}
        <svg
          ref={svgRef}
          className="w-full h-[560px] bg-card/30 cursor-grab active:cursor-grabbing"
        />
      </Card>
    </div>
  );
}

export default function GraphPage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-6">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-9 w-full max-w-md" />
          <Skeleton className="h-[560px] w-full rounded-lg" />
        </div>
      }
    >
      <GraphContent />
    </Suspense>
  );
}

