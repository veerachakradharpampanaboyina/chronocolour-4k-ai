"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { healthCheck, listVideos, listJobs } from "@/lib/api";
import type { Video, Job } from "@/types";

const STATUS_STYLES: Record<string, string> = {
  running: "bg-cyan/10 text-cyan border-cyan/20",
  completed: "bg-emerald/10 text-emerald border-emerald/20",
  queued: "bg-amber/10 text-amber border-amber/20",
  pending: "bg-amber/10 text-amber border-amber/20",
  failed: "bg-rose/10 text-rose border-rose/20",
  cancelled: "bg-text-muted/10 text-text-muted border-text-muted/20",
  uploading: "bg-cyan/10 text-cyan border-cyan/20",
  uploaded: "bg-emerald/10 text-emerald border-emerald/20",
  analyzing: "bg-cyan/10 text-cyan border-cyan/20",
  analyzed: "bg-emerald/10 text-emerald border-emerald/20",
  processing: "bg-accent/10 text-accent border-accent/20",
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const [videos, setVideos] = useState<Video[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalVideos, setTotalVideos] = useState(0);
  const [totalJobs, setTotalJobs] = useState(0);
  const [health, setHealth] = useState<{ status: string; checks: Record<string, string> } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setMounted(true);
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const [videosRes, jobsRes, healthRes] = await Promise.allSettled([
        listVideos(1, 10),
        listJobs(1, 10),
        healthCheck(),
      ]);

      if (videosRes.status === "fulfilled") {
        setVideos(videosRes.value.videos);
        setTotalVideos(videosRes.value.total);
      }
      if (jobsRes.status === "fulfilled") {
        setJobs(jobsRes.value.jobs);
        setTotalJobs(jobsRes.value.total);
      }
      if (healthRes.status === "fulfilled") {
        setHealth(healthRes.value);
      }
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  }

  const completedJobs = jobs.filter((j) => j.status === "completed").length;
  const runningJobs = jobs.filter((j) => j.status === "running").length;
  const activeJob = jobs.find((j) => j.status === "running");

  const stats = [
    { label: "Total Videos", value: String(totalVideos), change: `${videos.length} recent`, icon: "🎬", color: "from-accent to-indigo" },
    { label: "Total Jobs", value: String(totalJobs), change: `${completedJobs} completed`, icon: "⚡", color: "from-cyan to-emerald" },
    { label: "Running Jobs", value: String(runningJobs), change: runningJobs > 0 ? "Processing now" : "Idle", icon: "🔄", color: "from-emerald to-cyan" },
    {
      label: "System Health",
      value: health ? (health.status === "healthy" ? "✓" : "⚠") : "—",
      change: health ? health.status : "Checking...",
      icon: "🖥️",
      color: "from-amber to-rose",
    },
  ];

  return (
    <div className="space-y-8">
      {/* ---- Stats Cards ---- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
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
              {loading && (
                <div className="w-3 h-3 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
              )}
            </div>
            <div className="text-2xl font-bold mb-0.5">{loading ? "—" : stat.value}</div>
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

        {/* Active Pipeline or Empty State */}
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Active Pipeline</h3>
            {activeJob && (
              <span className="text-xs text-text-muted">{activeJob.video_filename}</span>
            )}
          </div>

          {activeJob ? (
            <>
              <div className="grid grid-cols-8 gap-1.5">
                {(activeJob.stages || []).slice(0, 8).map((stage) => (
                  <div key={stage.stage} className="text-center">
                    <div
                      className={`h-2 rounded-full mb-1.5 ${
                        stage.status === "completed"
                          ? "bg-gradient-to-r from-emerald to-cyan"
                          : stage.status === "running"
                          ? "bg-accent shimmer"
                          : "bg-bg-tertiary"
                      }`}
                    />
                    <span className="text-[9px] text-text-muted leading-tight block truncate">
                      {stage.stage_display_name || stage.stage}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center gap-3">
                <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-accent via-cyan to-emerald rounded-full transition-all duration-1000 shimmer"
                    style={{ width: `${activeJob.overall_progress}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-accent-light">
                  {activeJob.overall_progress.toFixed(0)}%
                </span>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-text-muted">
              <div className="text-3xl mb-2">🎬</div>
              <p className="text-sm">No active pipeline. Upload a video to get started.</p>
            </div>
          )}
        </div>
      </div>

      {/* ---- Service Health ---- */}
      {health && (
        <div className="glass-card p-5">
          <h3 className="font-semibold mb-3">Service Status</h3>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(health.checks).map(([service, status]) => (
              <div key={service} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-bg-tertiary/30">
                <span
                  className={`w-2 h-2 rounded-full ${
                    status === "healthy" ? "bg-emerald animate-pulse" : "bg-rose"
                  }`}
                />
                <span className="text-xs font-medium capitalize">{service}</span>
                <span className={`ml-auto text-[10px] ${status === "healthy" ? "text-emerald" : "text-rose"}`}>
                  {status === "healthy" ? "Online" : "Offline"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ---- Recent Videos ---- */}
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <h3 className="font-semibold">Recent Videos</h3>
          <button
            onClick={loadDashboardData}
            className="text-xs text-accent-light hover:text-accent transition-colors"
          >
            ↻ Refresh
          </button>
        </div>

        {videos.length > 0 ? (
          <div className="divide-y divide-border">
            {videos.map((video, i) => (
              <div
                key={video.id}
                className={`flex items-center gap-4 px-5 py-3.5 hover:bg-bg-tertiary/30 transition-colors ${
                  mounted ? "opacity-100" : "opacity-0"
                }`}
                style={{ transitionDelay: `${(i + 4) * 80}ms`, transition: "opacity 0.5s" }}
              >
                <div className="w-8 h-8 rounded-lg bg-bg-tertiary flex items-center justify-center text-sm">
                  🎬
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{video.original_filename}</div>
                  <div className="text-xs text-text-muted">
                    {formatBytes(video.file_size_bytes)} • {timeAgo(video.created_at)}
                  </div>
                </div>
                <span
                  className={`text-[10px] font-medium px-2.5 py-1 rounded-full border capitalize ${
                    STATUS_STYLES[video.status] || ""
                  }`}
                >
                  {video.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-12 text-center text-text-muted">
            <div className="text-4xl mb-3">📭</div>
            <div className="text-sm">No videos uploaded yet</div>
            <Link
              href="/dashboard/upload"
              className="inline-block mt-4 px-5 py-2 bg-gradient-to-r from-accent to-cyan text-white text-xs font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              Upload Your First Video
            </Link>
          </div>
        )}
      </div>

      {/* ---- Recent Jobs ---- */}
      {jobs.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div className="flex items-center justify-between p-5 border-b border-border">
            <h3 className="font-semibold">Recent Jobs</h3>
            <Link href="/dashboard/jobs" className="text-xs text-accent-light hover:text-accent transition-colors">
              View All →
            </Link>
          </div>
          <div className="divide-y divide-border">
            {jobs.slice(0, 5).map((job) => (
              <Link
                key={job.id}
                href={`/dashboard/jobs/${job.id}`}
                className="flex items-center gap-4 px-5 py-3.5 hover:bg-bg-tertiary/30 transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-bg-tertiary flex items-center justify-center text-sm">
                  ⚡
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{job.video_filename}</div>
                  <div className="text-xs text-text-muted">
                    {job.current_stage_display_name || job.current_stage || "Pending"} • {timeAgo(job.created_at)}
                  </div>
                </div>
                <div className="w-28 hidden sm:block">
                  {job.status === "running" && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-accent to-cyan rounded-full shimmer"
                          style={{ width: `${job.overall_progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-accent-light font-mono">{job.overall_progress}%</span>
                    </div>
                  )}
                </div>
                <span
                  className={`text-[10px] font-medium px-2.5 py-1 rounded-full border capitalize ${
                    STATUS_STYLES[job.status] || ""
                  }`}
                >
                  {job.status}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
