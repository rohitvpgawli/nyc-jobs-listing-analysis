import { useEffect, useRef, useState } from "react";

/**
 * Reveal-on-scroll: IntersectionObserver when available, plus a passive
 * scroll/resize fallback (some embedded webviews throttle IO callbacks).
 */
export function useReveal<T extends HTMLElement>(threshold = 0.25) {
  const ref = useRef<T | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (el == null || visible) return;

    let done = false;
    const trigger = () => {
      if (done) return;
      done = true;
      setVisible(true);
      cleanup();
    };

    const check = () => {
      const r = el.getBoundingClientRect();
      const vh = window.innerHeight || document.documentElement.clientHeight;
      const visiblePx = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      if (visiblePx >= Math.min(r.height, vh) * threshold) trigger();
    };

    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) trigger();
      },
      { threshold: Math.min(threshold, 0.5) }
    );
    obs.observe(el);

    window.addEventListener("scroll", check, { passive: true });
    window.addEventListener("resize", check, { passive: true });
    const interval = window.setInterval(check, 500);

    const cleanup = () => {
      obs.disconnect();
      window.removeEventListener("scroll", check);
      window.removeEventListener("resize", check);
      window.clearInterval(interval);
    };

    check();
    return cleanup;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [threshold]);

  return { ref, visible };
}
