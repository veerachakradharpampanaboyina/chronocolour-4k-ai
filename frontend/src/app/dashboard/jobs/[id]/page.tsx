"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const STAGE_STATUS_ICON: Record<string, string> = {
  completed: "✅",
  running: "🔄",
  pending: "⏳",
  failed: "❌",
  skipped: "⏭️",
};

const DEMO_STAGES = [
  { stage: "analyze", name: "Video Analysis", status: "completed", progress: 100, duration: "12s", message: "480p, 24fps, 1440 frames" },
  { stage: "restore", name: "Frame Restoration", status: "completed", progress: 100, duration: "8m 23s", message: "NAFNet denoising applied" },
  { stage: "super_resolution", name: "4K Super Resolution", status: "completed", progress: 100, duration: "45m 12s", message: "Real-ESRGAN 4x upscale" },
  { stage: "face_restoration", name: "Face Restoration", status: "completed", progress: 100, duration: "15m 34s", message: "127 faces restored with CodeFormer" },
  { stage: "scene_understanding", name: "Scene Understanding", status: "completed", progress: 100, duration: "2m 8s", message: "Dominant: outdoor/city" },
  { stage: "object_detection", name: "Object Detection", status: "completed", progress: 100, duration: "6m 45s", message: "3,842 detections across 1440 frames" },
  { stage: "object_tracking", name: "Object Tracking", status: "completed", progress: 100, duration: "3m 12s", message: "24 unique tracks (Person, Car, Building)" },
  { stage: "segmentation", name: "Semantic Segmentation", status: "completed", progress: 100, duration: "18m 56s", message: "SAM 2 masks for all tracked objects" },
  { stage: "colorization", name: "AI Colorization", status: "running", progress: 67, duration: "32m", message: "DDColor processing frame 964/1440..." },
  { stage: "temporal_memory", name: "Temporal Color Memory", status: "pending", progress: 0, duration: "—", message: "" },
  { stage: "optical_flow", name: "Optical Flow", status: "pending", progress: 0, duration: "—", message: "" },
  { stage: "flicker_correction", name: "Flicker Correction", status: "pending", progress: 0, duration: "—", message: "" },
  { stage: "hdr_enhancement", name: "HDR Enhancement", status: "pending", progress: 0, duration: "—", message: "" },
  { stage: "quality_assessment", name: "Quality Assessment", status: "pending", progress: 0, duration: "—", message: "" },
  { stage: "reconstruction", name: "Video Reconstruction", status: "pending", progress: 0, duration: "—", message: "" },
  { stage: "audio_sync", name: "Audio Synchronization", status: "pending", progress: 0, duration: "—", message: "" },
];

export default function JobDetailPage() {
  const [overallProgress, setOverallProgress] = useState(67);
  const [elapsed, setElapsed] = useState("2h 14m");

  // Simulate progress animation
  useEffect(() => {
    const interval = setInterval(() => {
      setOverallProgress((p) => Math.min(p + 0.1, 68));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* ---- Header ---- */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/dashboard/jobs" className="text-xs text-text-muted hover:text-accent-light mb-2 inline-block">
            ← Back to Jobs
          </Link>
          <h1 className="text-2xl font-bold">old_film_1924.mp4</h1>
          <div className="flex items-center gap-4 mt-2 text-sm text-text-muted">
            <span>480p → 4K</span>
            <span>•</span>
            <span>1440 frames</span>
            <span>•</span>
            <span>Balanced preset</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 border border-border rounded-lg text-sm text-text-secondary hover:border-rose/50 hover:text-rose transition-colors">
            Cancel
          </button>
        </div>
      </div>

      {/* ---- Overall Progress ---- */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="ml-3 text-xs text-text-muted">ETA: ~1h 20m remaining</span>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold gradient-text">{overallProgress.toFixed(1)}%</span>
            <div className="text-xs text-text-muted">{elapsed} elapsed</div>
          </div>
        </div>
        <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-accent via-cyan to-emerald rounded-full transition-all duration-1000 shimmer"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      {/* ---- Pipeline Stages ---- */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-5">Pipeline Stages</h2>
        <div className="space-y-1">
          {DEMO_STAGES.map((stage, i) => (
            <div
              key={stage.stage}
              className={`flex items-center gap-4 px-4 py-3 rounded-lg transition-all ${
                stage.status === "running"
                  ? "bg-accent/5 border border-accent/20"
                  : stage.status === "completed"
                  ? "hover:bg-bg-tertiary/30"
                  : "opacity-50"
              }`}
            >
              {/* Stage Number */}
              <span className="text-xs font-mono text-text-muted w-6 text-right shrink-0">
                {String(i + 1).padStart(2, "0")}
              </span>

              {/* Status Icon */}
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm shrink-0 ${
                stage.status === "running" ? "animate-spin" : ""
              }`}>
                {STAGE_STATUS_ICON[stage.status] || "⏳"}
              </div>

              {/* Stage Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{stage.name}</span>
                  {stage.status === "running" && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan/10 text-cyan border border-cyan/20 animate-pulse">
                      Processing
                    </span>
                  )}
                </div>
                {stage.message && (
                  <p className="text-xs text-text-muted mt-0.5 truncate">{stage.message}</p>
                )}
              </div>

              {/* Progress */}
              {stage.status === "running" && (
                <div className="w-24 flex items-center gap-2 shrink-0">
                  <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-accent to-cyan rounded-full shimmer"
                      style={{ width: `${stage.progress}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono text-accent-light">{stage.progress}%</span>
                </div>
              )}

              {/* Duration */}
              <span className="text-xs text-text-muted w-16 text-right shrink-0 hidden sm:block">
                {stage.duration}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ---- Processing Info ---- */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Input Resolution", value: "480p" },
          { label: "Output Resolution", value: "3840×2160" },
          { label: "Total Frames", value: "1,440" },
          { label: "GPU Memory", value: "18.2 / 24 GB" },
        ].map((info) => (
          <div key={info.label} className="glass-card p-4 text-center">
            <div className="text-lg font-bold">{info.value}</div>
            <div className="text-xs text-text-muted mt-1">{info.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
