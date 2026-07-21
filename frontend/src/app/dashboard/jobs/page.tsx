"use client";

import Link from "next/link";
import { useState } from "react";

const STATUS_STYLES: Record<string, string> = {
  running: "bg-cyan/10 text-cyan border-cyan/20",
  completed: "bg-emerald/10 text-emerald border-emerald/20",
  queued: "bg-amber/10 text-amber border-amber/20",
  pending: "bg-amber/10 text-amber border-amber/20",
  failed: "bg-rose/10 text-rose border-rose/20",
  cancelled: "bg-text-muted/10 text-text-muted border-text-muted/20",
};

const DEMO_JOBS = [
  { id: "j1", filename: "old_film_1924.mp4", status: "running", progress: 67, stage: "AI Colorization", resolution: "4K", preset: "Balanced", created: "2 hours ago", duration: "2h 14m" },
  { id: "j2", filename: "family_1960s.avi", status: "completed", progress: 100, stage: "Complete", resolution: "4K", preset: "Maximum", created: "5 hours ago", duration: "4h 32m" },
  { id: "j3", filename: "ww2_footage.mkv", status: "queued", progress: 0, stage: "Pending", resolution: "4K", preset: "Balanced", created: "30 min ago", duration: "—" },
  { id: "j4", filename: "charlie_chaplin_modern_times.mp4", status: "completed", progress: 100, stage: "Complete", resolution: "1080p", preset: "Fast", created: "1 day ago", duration: "1h 58m" },
  { id: "j5", filename: "moon_landing_1969.mp4", status: "failed", progress: 42, stage: "Super Resolution", resolution: "4K", preset: "Balanced", created: "3 hours ago", duration: "1h 12m" },
  { id: "j6", filename: "elvis_concert_1956.mp4", status: "completed", progress: 100, stage: "Complete", resolution: "4K", preset: "Balanced", created: "2 days ago", duration: "3h 45m" },
  { id: "j7", filename: "titanic_departure.mp4", status: "cancelled", progress: 23, stage: "Frame Restoration", resolution: "4K", preset: "Maximum", created: "1 day ago", duration: "45m" },
];

const FILTER_TABS = ["All", "Running", "Completed", "Queued", "Failed"];

export default function JobsPage() {
  const [activeFilter, setActiveFilter] = useState("All");

  const filteredJobs =
    activeFilter === "All"
      ? DEMO_JOBS
      : DEMO_JOBS.filter((j) => j.status === activeFilter.toLowerCase());

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Processing Jobs</h1>
          <p className="text-sm text-text-muted mt-1">{DEMO_JOBS.length} total jobs</p>
        </div>
        <Link
          href="/dashboard/upload"
          className="px-5 py-2 bg-gradient-to-r from-accent to-cyan text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
        >
          + New Job
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        {FILTER_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveFilter(tab)}
            className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeFilter === tab
                ? "bg-accent/15 text-accent-light border border-accent/20"
                : "text-text-muted hover:text-text-primary hover:bg-bg-tertiary"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Jobs Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left text-xs font-medium text-text-muted px-5 py-3">Video</th>
              <th className="text-left text-xs font-medium text-text-muted px-5 py-3 hidden md:table-cell">Resolution</th>
              <th className="text-left text-xs font-medium text-text-muted px-5 py-3 hidden lg:table-cell">Preset</th>
              <th className="text-left text-xs font-medium text-text-muted px-5 py-3">Progress</th>
              <th className="text-left text-xs font-medium text-text-muted px-5 py-3 hidden sm:table-cell">Duration</th>
              <th className="text-left text-xs font-medium text-text-muted px-5 py-3">Status</th>
              <th className="text-right text-xs font-medium text-text-muted px-5 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filteredJobs.map((job) => (
              <tr key={job.id} className="hover:bg-bg-tertiary/30 transition-colors">
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-bg-tertiary flex items-center justify-center text-sm shrink-0">
                      🎬
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-medium truncate max-w-[200px]">{job.filename}</div>
                      <div className="text-[11px] text-text-muted">{job.stage} • {job.created}</div>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3.5 hidden md:table-cell">
                  <span className="text-xs font-mono text-text-secondary">{job.resolution}</span>
                </td>
                <td className="px-5 py-3.5 hidden lg:table-cell">
                  <span className="text-xs text-text-secondary">{job.preset}</span>
                </td>
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2 w-28">
                    <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          job.status === "completed"
                            ? "bg-emerald"
                            : job.status === "failed"
                            ? "bg-rose"
                            : job.status === "running"
                            ? "bg-gradient-to-r from-accent to-cyan shimmer"
                            : "bg-amber/40"
                        }`}
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-text-muted w-8">{job.progress}%</span>
                  </div>
                </td>
                <td className="px-5 py-3.5 text-xs text-text-muted hidden sm:table-cell">{job.duration}</td>
                <td className="px-5 py-3.5">
                  <span className={`text-[10px] font-medium px-2.5 py-1 rounded-full border capitalize ${STATUS_STYLES[job.status] || ""}`}>
                    {job.status}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-right">
                  <Link
                    href={`/dashboard/jobs/${job.id}`}
                    className="text-xs text-accent-light hover:text-accent transition-colors"
                  >
                    View →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredJobs.length === 0 && (
          <div className="py-16 text-center text-text-muted">
            <div className="text-4xl mb-3">📭</div>
            <div className="text-sm">No {activeFilter.toLowerCase()} jobs found</div>
          </div>
        )}
      </div>
    </div>
  );
}
