"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const PIPELINE_STAGES = [
  { icon: "📹", name: "Video Analysis", desc: "Resolution, FPS, damage detection" },
  { icon: "🧹", name: "Frame Restoration", desc: "Scratch, dust, noise removal" },
  { icon: "🔍", name: "4K Super Resolution", desc: "Progressive upscaling to 4K" },
  { icon: "👤", name: "Face Restoration", desc: "GFPGAN / CodeFormer enhancement" },
  { icon: "🌅", name: "Scene Understanding", desc: "Beach, forest, city, night context" },
  { icon: "🎯", name: "Object Detection", desc: "YOLOv11 person, car, tree detection" },
  { icon: "🔗", name: "Object Tracking", desc: "Persistent IDs across frames" },
  { icon: "✂️", name: "Segmentation", desc: "SAM 2 pixel-precise masks" },
  { icon: "🎨", name: "AI Colorization", desc: "DDColor semantic color prediction" },
  { icon: "🧠", name: "Color Memory", desc: "Temporal consistency enforcement" },
  { icon: "🌊", name: "Optical Flow", desc: "RAFT motion-guided propagation" },
  { icon: "⚡", name: "Flicker Correction", desc: "Frame-to-frame smoothing" },
  { icon: "🌈", name: "HDR Enhancement", desc: "Dynamic range expansion" },
  { icon: "📊", name: "Quality Assessment", desc: "BRISQUE scoring per frame" },
  { icon: "🎬", name: "Video Reconstruction", desc: "HEVC 4K encoding" },
  { icon: "🔊", name: "Audio Sync", desc: "Original audio preservation" },
];

const STATS = [
  { value: "16", label: "AI Pipeline Stages" },
  { value: "15+", label: "AI Models Integrated" },
  { value: "4K", label: "Output Resolution" },
  { value: "HDR", label: "Color Depth" },
];

export default function LandingPage() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % PIPELINE_STAGES.length);
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* ---- Navigation ---- */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-bg-primary/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-cyan flex items-center justify-center text-sm font-bold">
              CC
            </div>
            <span className="font-semibold text-lg">ChronoColor <span className="text-accent-light">4K AI</span></span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-text-secondary">
            <a href="#pipeline" className="hover:text-text-primary transition-colors">Pipeline</a>
            <a href="#features" className="hover:text-text-primary transition-colors">Features</a>
            <a href="#tech" className="hover:text-text-primary transition-colors">Technology</a>
          </div>
          <Link
            href="/dashboard"
            className="px-5 py-2 bg-gradient-to-r from-accent to-cyan text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity shadow-lg shadow-accent/20"
          >
            Launch Dashboard
          </Link>
        </div>
      </nav>

      {/* ---- Hero ---- */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Background glow effects */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-[128px] pointer-events-none" />
        <div className="absolute top-40 right-1/4 w-80 h-80 bg-cyan/10 rounded-full blur-[128px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-6 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5 text-accent-light text-xs font-medium mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald animate-pulse" />
            Powered by 15+ State-of-the-Art AI Models
          </div>

          <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6 max-w-4xl mx-auto">
            Transform B&W Videos into{" "}
            <span className="gradient-text">Cinematic 4K Color</span>{" "}
            Masterpieces
          </h1>

          <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed">
            The most advanced AI video colorization pipeline. Restore, upscale,
            detect, track, segment, and colorize — all in one seamless workflow.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link
              href="/dashboard/upload"
              className="px-8 py-3.5 bg-gradient-to-r from-accent via-indigo to-cyan text-white font-semibold rounded-xl hover:opacity-90 transition-all shadow-2xl shadow-accent/30 text-lg"
            >
              Start Colorizing →
            </Link>
            <a
              href="#pipeline"
              className="px-8 py-3.5 border border-border text-text-secondary font-medium rounded-xl hover:border-accent/50 hover:text-text-primary transition-all"
            >
              See Pipeline
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
            {STATS.map((stat) => (
              <div key={stat.label} className="glass-card p-4 text-center">
                <div className="text-3xl font-bold gradient-text">{stat.value}</div>
                <div className="text-xs text-text-muted mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- Pipeline Visualization ---- */}
      <section id="pipeline" className="py-20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Complete AI <span className="gradient-text">Pipeline</span>
            </h2>
            <p className="text-text-secondary max-w-xl mx-auto">
              16 sequential stages powered by state-of-the-art models,
              orchestrated for maximum quality.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {PIPELINE_STAGES.map((stage, i) => (
              <div
                key={stage.name}
                className={`glass-card p-4 cursor-pointer transition-all duration-500 ${
                  i === activeStage
                    ? "border-accent/60 shadow-lg shadow-accent/10 scale-[1.02]"
                    : i < activeStage
                    ? "border-emerald/30 opacity-80"
                    : "opacity-60"
                }`}
                onMouseEnter={() => setActiveStage(i)}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0 ${
                      i === activeStage
                        ? "bg-accent/20"
                        : i < activeStage
                        ? "bg-emerald/10"
                        : "bg-bg-tertiary"
                    }`}
                  >
                    {stage.icon}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-text-muted font-mono">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <h3 className="text-sm font-semibold">{stage.name}</h3>
                    </div>
                    <p className="text-xs text-text-muted mt-0.5">{stage.desc}</p>
                  </div>
                </div>
                {i === activeStage && (
                  <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-accent to-cyan shimmer" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- Features ---- */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: "🎯",
                title: "Semantic Colorization",
                desc: "Colors are predicted per-object, not per-pixel. Person_001's blue shirt stays blue across all 2400 frames.",
                color: "from-accent to-indigo",
              },
              {
                icon: "🧠",
                title: "Temporal Memory",
                desc: "A color database maintains RGB values for every tracked object, preventing sudden color shifts between frames.",
                color: "from-cyan to-emerald",
              },
              {
                icon: "⚡",
                title: "Progressive 4K",
                desc: "Upscale before colorizing — 480p → 720p → 1080p → 4K — so the AI has maximum detail to work with.",
                color: "from-amber to-rose",
              },
            ].map((feature) => (
              <div key={feature.title} className="glass-card p-8 group">
                <div
                  className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform`}
                >
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-text-secondary text-sm leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- Technology ---- */}
      <section id="tech" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Built with <span className="gradient-text">Cutting-Edge</span> Technology
            </h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {[
              "PyTorch", "FastAPI", "Celery", "Redis", "MongoDB", "FFmpeg",
              "Real-ESRGAN", "GFPGAN", "CodeFormer", "YOLOv11", "SAM 2", "DDColor",
              "RAFT", "ByteTrack", "NAFNet", "Next.js 15", "Docker", "MinIO",
            ].map((tech) => (
              <div
                key={tech}
                className="glass-card px-4 py-3 text-center text-sm font-medium hover:border-accent/50 transition-colors"
              >
                {tech}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- CTA ---- */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <div className="gradient-border p-12 rounded-2xl">
            <h2 className="text-3xl font-bold mb-4">Ready to Bring History to Life?</h2>
            <p className="text-text-secondary mb-8">
              Upload your black & white video and watch AI transform it into a cinematic 4K color masterpiece.
            </p>
            <Link
              href="/dashboard/upload"
              className="inline-flex px-8 py-3.5 bg-gradient-to-r from-accent to-cyan text-white font-semibold rounded-xl hover:opacity-90 transition-all shadow-2xl shadow-accent/30 text-lg"
            >
              Launch Dashboard →
            </Link>
          </div>
        </div>
      </section>

      {/* ---- Footer ---- */}
      <footer className="border-t border-border py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-text-muted">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-accent to-cyan flex items-center justify-center text-[10px] font-bold text-white">
              CC
            </div>
            ChronoColor 4K AI — © 2026
          </div>
          <div className="text-xs text-text-muted">
            Powered by PyTorch • Real-ESRGAN • DDColor • SAM 2 • YOLOv11
          </div>
        </div>
      </footer>
    </div>
  );
}
