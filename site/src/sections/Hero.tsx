import { useEffect, useRef, useState } from "react";
import { atlas } from "../lib/data";

function useCountUp(target: number, duration = 1600, start = false) {
  const [value, setValue] = useState(0);
  const raf = useRef(0);
  useEffect(() => {
    if (!start) return;
    const t0 = performance.now();
    const tick = (t: number) => {
      const p = Math.min((t - t0) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setValue(Math.round(target * eased));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [target, duration, start]);
  return value;
}

export default function Hero() {
  const [go, setGo] = useState(false);
  useEffect(() => {
    const id = setTimeout(() => setGo(true), 350);
    return () => clearTimeout(id);
  }, []);

  const jobs = useCountUp(atlas.meta.jobCount, 1600, go);
  const companies = useCountUp(atlas.meta.companyCount, 1600, go);
  const operatorShare = Math.round(
    (atlas.jobs.filter((j) => j.operatorAdjacent).length / atlas.jobs.length) * 100
  );
  const share = useCountUp(operatorShare, 1900, go);

  return (
    <section className="hero">
      <div className="wrap">
        <div className="hero-badge">
          <span className="hero-dot" style={{ background: "var(--yellow)" }} />
          <span className="hero-dot" style={{ background: "var(--red)" }} />
          <span className="hero-dot" style={{ background: "var(--blue)" }} />
          <span className="hero-badge-text">NYC AI STARTUP HIRING ATLAS · {atlas.meta.collectedAt}</span>
        </div>
        <h1 className="hero-title">
          <span className="hero-line1">The Hiring</span>
          <span className="hero-line2">Signal<span style={{ color: "var(--yellow)" }}>.</span></span>
        </h1>
        <p className="hero-sub">
          Every AI company says it's building the future.
          <br />
          <strong>Their job boards say what they're building it with.</strong>
        </p>

        <div className="hero-stats">
          <div className="hero-stat">
            <div className="hero-stat-num">{jobs}</div>
            <div className="hero-stat-label">open roles, classified</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-num">{companies}</div>
            <div className="hero-stat-label">YC-backed AI startups in NYC</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-num">{share}<span className="hero-stat-pct">%</span></div>
            <div className="hero-stat-label">are core data/AI-operator roles</div>
          </div>
        </div>

        <div className="hero-scroll">scroll ↓</div>
      </div>
    </section>
  );
}
