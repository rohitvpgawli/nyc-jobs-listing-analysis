import { useMemo } from "react";
import { sankey, sankeyLinkHorizontal, SankeyNode, SankeyLink } from "d3-sankey";
import { atlas } from "../lib/data";
import { CATEGORY_COLORS, CATEGORY_LABELS, FAMILY_META, NEED_LABELS } from "../lib/theme";
import { useReveal } from "../lib/useReveal";
import { useTooltip } from "../lib/useTooltip";

interface NodeDatum {
  id: string;
  label: string;
  color: string;
  kind: "category" | "family" | "need";
}
type SNode = SankeyNode<NodeDatum, {}>;
type SLink = SankeyLink<NodeDatum, {}>;

const TOP_FAMILIES = 6;
const TOP_NEEDS = 8;
const WIDTH = 1020;
const HEIGHT = 620;

export default function HiddenStructure() {
  const { ref, visible } = useReveal<HTMLDivElement>(0.15);
  const { show, hide, node } = useTooltip();

  const graph = useMemo(() => {
    const famTotals = new Map<string, number>();
    for (const j of atlas.jobs) famTotals.set(j.family, (famTotals.get(j.family) ?? 0) + 1);
    const topFams = [...famTotals.entries()].sort((a, b) => b[1] - a[1]).slice(0, TOP_FAMILIES).map(([f]) => f);

    const needTotals = new Map<string, number>();
    for (const j of atlas.jobs) for (const t of j.needTags) needTotals.set(t, (needTotals.get(t) ?? 0) + 1);
    const topNeeds = [...needTotals.entries()].sort((a, b) => b[1] - a[1]).slice(0, TOP_NEEDS).map(([t]) => t);

    const catFlow = new Map<string, number>(); // cat|fam -> jobs
    const needFlow = new Map<string, number>(); // fam|need -> normalized weight
    for (const j of atlas.jobs) {
      const fam = topFams.includes(j.family) ? j.family : "__other_fam";
      catFlow.set(`${j.aiCategory}|${fam}`, (catFlow.get(`${j.aiCategory}|${fam}`) ?? 0) + 1);
      const tags = j.needTags.filter((t) => topNeeds.includes(t));
      if (tags.length === 0) continue;
      // Normalize multi-tag roles so each job contributes 1 unit of flow.
      const w = 1 / tags.length;
      for (const t of tags) needFlow.set(`${fam}|${t}`, (needFlow.get(`${fam}|${t}`) ?? 0) + w);
    }

    const nodes: NodeDatum[] = [];
    const idx = new Map<string, number>();
    const addNode = (n: NodeDatum) => {
      if (!idx.has(n.id)) {
        idx.set(n.id, nodes.length);
        nodes.push(n);
      }
      return idx.get(n.id)!;
    };

    const links: { source: number; target: number; value: number }[] = [];
    for (const [key, value] of catFlow) {
      const [cat, fam] = key.split("|");
      if (value < 3) continue; // prune spaghetti
      const s = addNode({ id: `c:${cat}`, label: CATEGORY_LABELS[cat] ?? cat, color: CATEGORY_COLORS[cat] ?? "#666", kind: "category" });
      const famMeta = FAMILY_META[fam];
      const t = addNode({
        id: `f:${fam}`,
        label: fam === "__other_fam" ? "Other families" : famMeta.short,
        color: fam === "__other_fam" ? "#58595B" : famMeta.color,
        kind: "family",
      });
      links.push({ source: s, target: t, value });
    }
    for (const [key, value] of needFlow) {
      const [fam, need] = key.split("|");
      if (value < 3 || !idx.has(`f:${fam}`)) continue;
      const s = idx.get(`f:${fam}`)!;
      const t = addNode({ id: `n:${need}`, label: NEED_LABELS[need] ?? need, color: "#f4f1ea", kind: "need" });
      links.push({ source: s, target: t, value });
    }

    const gen = sankey<NodeDatum, {}>()
      .nodeWidth(14)
      .nodePadding(14)
      // leave room on the right for the operator-need labels
      .extent([[0, 20], [WIDTH - 210, HEIGHT - 20]]);
    return gen({ nodes: nodes.map((d) => ({ ...d })), links: links.map((d) => ({ ...d })) });
  }, []);

  const path = sankeyLinkHorizontal();

  return (
    <section id="structure">
      <div className="wrap">
        <div className="kicker">02 · The hidden structure</div>
        <h2>Follow a job posting from pitch to plumbing.</h2>
        <p className="lede">
          Left: what the startup sells. Middle: who they hire. Right: <strong>the operating problem
          buried in the job description</strong>. Whatever the vertical, the flows converge on the same
          demands — agent workflows, infrastructure, customer implementation, reporting.
        </p>

        <div ref={ref} className={`reveal ${visible ? "is-visible" : ""}`} style={{ overflowX: "auto" }}>
          <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} style={{ width: "100%", minWidth: 760, height: "auto" }}>
            <g>
              {(graph.links as SLink[]).map((l, i) => {
                const src = l.source as SNode;
                const tgt = l.target as SNode;
                return (
                  <path
                    key={i}
                    d={path(l) ?? ""}
                    fill="none"
                    stroke={src.color}
                    strokeOpacity={visible ? (src.kind === "category" ? 0.3 : 0.38) : 0}
                    strokeWidth={Math.max(1, l.width ?? 1)}
                    style={{ transition: `stroke-opacity 0.9s ease ${i * 12}ms` }}
                    onMouseMove={(e) =>
                      show(e, `<b>${src.label} → ${tgt.label}</b><br/>${Math.round(l.value as number)} roles`)
                    }
                    onMouseLeave={hide}
                  />
                );
              })}
            </g>
            <g>
              {(graph.nodes as SNode[]).map((n, i) => (
                <g key={i} style={{ opacity: visible ? 1 : 0, transition: `opacity 0.6s ease ${200 + i * 25}ms` }}>
                  <rect
                    x={n.x0}
                    y={n.y0}
                    width={(n.x1 ?? 0) - (n.x0 ?? 0)}
                    height={Math.max(1, (n.y1 ?? 0) - (n.y0 ?? 0))}
                    fill={n.color}
                    rx={2}
                    onMouseMove={(e) => show(e, `<b>${n.label}</b><br/>${Math.round(n.value ?? 0)} roles`)}
                    onMouseLeave={hide}
                  />
                  <text
                    x={(n.x1 ?? 0) + 8}
                    y={((n.y0 ?? 0) + (n.y1 ?? 0)) / 2}
                    dy="0.35em"
                    textAnchor="start"
                    fill="#f4f1ea"
                    fontSize={12.5}
                    fontWeight={n.kind === "family" ? 600 : 400}
                  >
                    {n.label}
                    {n.kind === "need" ? ` · ${Math.round(n.value ?? 0)}` : ""}
                  </text>
                </g>
              ))}
            </g>
          </svg>
          <div className="chart-note">
            AI category → role family → operator need. Multi-tag roles split their flow evenly across tags;
            flows under 3 roles pruned for legibility.
          </div>
        </div>
      </div>
      {node}
    </section>
  );
}
