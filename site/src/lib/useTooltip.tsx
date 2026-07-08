import { useCallback, useState } from "react";

interface TooltipState {
  x: number;
  y: number;
  html: string;
}

export function useTooltip() {
  const [tip, setTip] = useState<TooltipState | null>(null);

  const show = useCallback((event: { clientX: number; clientY: number }, html: string) => {
    const pad = 16;
    const x = Math.min(event.clientX + pad, window.innerWidth - 320);
    const y = Math.min(event.clientY + pad, window.innerHeight - 120);
    setTip({ x, y, html });
  }, []);

  const hide = useCallback(() => setTip(null), []);

  const node = tip ? (
    <div className="tooltip" style={{ left: tip.x, top: tip.y }} dangerouslySetInnerHTML={{ __html: tip.html }} />
  ) : null;

  return { show, hide, node };
}
