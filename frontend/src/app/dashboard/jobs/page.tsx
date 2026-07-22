"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listJobs, cancelJob } from "@/lib/api";
import type { Job } from "@/types";

const STATUS_STYLES: Record<string, string> = {
  running: "bg-cyan/10 text-cyan border-cyan/20",
  completed: "bg-emerald/10 text-emerald border-emerald/20",
  queued: "bg-amber/10 text-amber border-amber/20",
  pending: "bg-amber/10 text-amber border-amber/20",
  failed: "bg-rose/10 text-rose border-rose/20",
  cancelled: "bg-text-muted/10 text-text-muted border-text-muted/20",
};

const FILTER_TABS = ["All", "Running", "Completed", "Queued", "Failed"];

function timeAgo(dateStr: string): string {
  if (!dateStr) return "—";
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export default function JobsPage() {
  const [activeFilter, setActiveFilter] = useState("All");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchJobs();
  }, [activeFilter]);

  async function fetchJobs() {
    setLoading(true);
    setError(null);
    try {
      const statusParam = activeFilter !== "All" ? activeFilter.toLowerCase() : undefined;
      const res = await listJobs(1, 50, statusParam);
      setJobs(res.jobs);
      setTotal(res.total);
    } catch (err: any) {
      console.error("Failed to fetch jobs:", err);
      setError(err.message || "Failed to load jobs list.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(jobId: string, e: React.MouseEvent) {
    e.stopPropagation();
    e.preventDefault();
    if (!confirm("Are you sure you want to cancel this job?")) return;
    try {
      await cancelJob(jobId);
      fetchJobs();
    } catch (err: any) {
      alert(err.message || "Failed to cancel job.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Processing Jobs</h1>
          <p className="text-sm text-text-muted mt-1">{total} total jobs</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchJobs}
            className="px-4 py-2 border border-border rounded-lg text-xs text-text-secondary hover:text-text-primary transition-colors"
          >
            ↻ Refresh
          </button>
          <Link
            href="/dashboard/upload"
            className="px-5 py-2 bg-gradient-to-r from-accent to-cyan text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
          >
            + New Job
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose/10 border border-rose/20 text-rose text-sm">
          ⚠️ {error}
        </div>
      )}

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
        {loading ? (
          <div className="py-16 text-center text-text-muted">
            <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading jobs...
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left text-xs font-medium text-text-muted px-5 py-3">Video</th>
                <th className="text-left text-xs font-medium text-text-muted px-5 py-3 hidden md:table-cell">Resolution</th>
                <th className="text-left text-xs font-medium text-text-muted px-5 py-3 hidden lg:table-cell">Preset</th>
                <th className="text-left text-xs font-medium text-text-muted px-5 py-3">Progress</th>
                <th className="text-left text-xs font-medium text-text-muted px-5 py-3 hidden sm:table-cell">Created</th>
                <th className="text-left text-xs font-medium text-text-muted px-5 py-3">Status</th>
                <th className="text-right text-xs font-medium text-text-muted px-5 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-bg-tertiary/30 transition-colors">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-bg-tertiary flex items-center justify-center text-sm shrink-0">
                        🎬
                      </div>
                      <div className="min-w-0">
                        <div className="text-sm font-medium truncate max-w-[200px]">{job.video_filename}</div>
                        <div className="text-[11px] text-text-muted truncate max-w-[200px]">
                          {job.current_stage_display_name || job.current_stage || "Queued"}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 hidden md:table-cell">
                    <span className="text-xs font-mono text-text-secondary">
                      {job.pipeline_config?.target_resolution || "4K"}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 hidden lg:table-cell">
                    <span className="text-xs text-text-secondary capitalize">
                      {job.pipeline_config?.quality_preset || "balanced"}
                    </span>
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
                          style={{ width: `${job.overall_progress}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-text-muted w-8">{job.overall_progress}%</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-text-muted hidden sm:table-cell">
                    {timeAgo(job.created_at)}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`text-[10px] font-medium px-2.5 py-1 rounded-full border capitalize ${STATUS_STYLES[job.status] || ""}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right space-x-3">
                    {(job.status === "running" || job.status === "queued" || job.status === "pending") && (
                      <button
                        onClick={(e) => handleCancel(job.id, e)}
                        className="text-xs text-rose/80 hover:text-rose transition-colors"
                      >
                        Cancel
                      </button>
                    )}
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
        )}

        {!loading && jobs.length === 0 && (
          <div className="py-16 text-center text-text-muted">
            <div className="text-4xl mb-3">📭</div>
            <div className="text-sm">No {activeFilter.toLowerCase()} jobs found</div>
            <Link
              href="/dashboard/upload"
              className="inline-block mt-4 px-4 py-2 bg-gradient-to-r from-accent to-cyan text-white text-xs font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              Start New Job
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
