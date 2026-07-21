"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface StatCard {
  label: string;
  value: string;
  change: string;
  icon: string;
  color: string;
}

const DEMO_STATS: StatCard[] = [
  { label: "Videos Processed", value: "47", change: "+12 this week", icon: "🎬", color: "from-accent to-indigo" },
  { label: "Total Minutes", value: "234", change: "38.2 hrs total", icon: "⏱️", color: "from-cyan to-emerald" },
  { label: "Avg Quality Score", value: "94.2", change: "↑ 2.1 from last week", icon: "📊", color: "from-emerald to-cyan" },
  { label: "GPU Hours", value: "186", change: "23.4 active hours", icon: "🖥️", color: "from-amber to-rose" },
];

const DEMO_JOBS = [
  { id: "1", filename: "old_film_1924.mp4", status: "running", progress: 67, stage: "AI Colorization", time: "2h 14m" },
  { id: "2", filename: "family_1960s.avi", status: "completed", progress: 100, stage: "Complete", time: "4h 32m" },
  { id: "3", filename: "ww2_footage.mkv", status: "queued", progress: 0, stage: "Pending", time: "—" },
  { id: "4", filename: "charlie_chaplin.mp4", status: "completed", progress: 100, stage: "Complete", time: "1h 58m" },
  { id: "5", filename: "moon_landing_69.mp4", status: "failed", progress: 42, stage: "Super Resolution", time: "1h 12m" },
];

const STATUS_STYLES: Record<string, string> = {
  running: "bg-cyan/10 text-cyan border-cyan/20",
  completed: "bg-emerald/10 text-emerald border-emerald/20",
  queued: "bg-amber/10 text-amber border-amber/20",
  pending: "bg-amber/10 text-amber border-amber/20",
  failed: "bg-rose/10 text-rose border-rose/20",
};

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="space-y-8">
      {/* ---- Stats Cards ---- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {DEMO_STATS.map((stat, i) => (
          <div
            key={stat.label}
            className={`glass-card p-5 group transition-all duration-500 ${
              mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            }`}
            style={{ transitionDelay: `${i * 100}ms` }}
          >
            <div className="flex items-start justify-between mb-3">
              <div
                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center text-lg group-hover:scale-110 transition-transform`}
              >
                {stat.icon}
              </div>
            </div>
            <div className="text-2xl font-bold mb-0.5">{stat.value}</div>
            <div className="text-xs text-text-muted">{stat.label}</div>
            <div className="text-[11px] text-accent-light mt-2">{stat.change}</div>
          </div>
        ))}
      </div>

      {/* ---- Quick Actions ---- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Link href="/dashboard/upload" className="lg:col-span-1">
          <div className="gradient-border p-8 h-full flex flex-col items-center justify-center text-center group cursor-pointer hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform">
              📤
            </div>
            <h3 className="text-lg font-semibold mb-1">Upload New Video</h3>
            <p className="text-sm text-text-muted">Drop a B&W video to start the AI pipeline</p>
          </div>
        </Link>

        {/* Pipeline Overview Mini */}
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Active Pipeline</h3>
            <span className="text-xs text-text-muted">old_film_1924.mp4</span>
          </div>
          <div className="grid grid-cols-8 gap-1.5">
            {[
              "Analysis", "Restore", "4K Upscale", "Face", "Scene", "Detect", "Color", "HDR",
            ].map((stage, i) => (
              <div key={stage} className="text-center">
                <div
                  className={`h-2 rounded-full mb-1.5 ${
                    i < 5
                      ? "bg-gradient-to-r from-emerald to-cyan"
                      : i === 5
                      ? "bg-accent shimmer"
                      : "bg-bg-tertiary"
                  }`}
                />
                <span className="text-[9px] text-text-muted leading-tight block">{stage}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center gap-3">
            <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-accent via-cyan to-emerald rounded-full transition-all duration-1000"
                style={{ width: "67%" }}
              />
            </div>
            <span className="text-sm font-semibold text-accent-light">67%</span>
          </div>
        </div>
      </div>

      {/* ---- Recent Jobs ---- */}
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <h3 className="font-semibold">Recent Jobs</h3>
          <Link href="/dashboard/jobs" className="text-xs text-accent-light hover:text-accent transition-colors">
            View All →
          </Link>
        </div>

        <div className="divide-y divide-border">
          {DEMO_JOBS.map((job, i) => (
            <div
              key={job.id}
              className={`flex items-center gap-4 px-5 py-3.5 hover:bg-bg-tertiary/30 transition-colors ${
                mounted ? "opacity-100" : "opacity-0"
              }`}
              style={{ transitionDelay: `${(i + 4) * 80}ms`, transition: "opacity 0.5s" }}
            >
              <div className="w-8 h-8 rounded-lg bg-bg-tertiary flex items-center justify-center text-sm">
                🎬
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{job.filename}</div>
                <div className="text-xs text-text-muted">{job.stage}</div>
              </div>
              <div className="w-32 hidden sm:block">
                {job.status === "running" && (
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-accent to-cyan rounded-full shimmer"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-accent-light font-mono">{job.progress}%</span>
                  </div>
                )}
              </div>
              <span className="text-xs text-text-muted w-16 text-right hidden md:block">{job.time}</span>
              <span
                className={`text-[10px] font-medium px-2.5 py-1 rounded-full border capitalize ${
                  STATUS_STYLES[job.status] || ""
                }`}
              >
                {job.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
