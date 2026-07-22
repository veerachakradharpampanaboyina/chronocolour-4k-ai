"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getJob, cancelJob, connectJobWebSocket } from "@/lib/api";
import type { Job, StageProgress } from "@/types";

const STAGE_STATUS_ICON: Record<string, string> = {
  completed: "✅",
  running: "🔄",
  pending: "⏳",
  failed: "❌",
  skipped: "⏭️",
};

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params?.id as string;

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    // Fetch initial job status
    fetchJobDetails();

    // Connect WebSocket for live progress
    const ws = connectJobWebSocket(jobId);

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "progress" || data.status) {
          // Re-fetch job details on updates
          fetchJobDetails();
        }
      } catch (err) {
        console.error("WS message parse error:", err);
      }
    };

    ws.onerror = () => {
      setWsConnected(false);
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [jobId]);

  async function fetchJobDetails() {
    try {
      const data = await getJob(jobId);
      setJob(data);
    } catch (err: any) {
      console.error("Failed to fetch job details:", err);
      setError(err.message || "Failed to load job details.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel() {
    if (!confirm("Are you sure you want to cancel this processing job?")) return;
    try {
      await cancelJob(jobId);
      fetchJobDetails();
    } catch (err: any) {
      alert(err.message || "Failed to cancel job.");
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-16 text-center text-text-muted">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading job details...
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-5xl mx-auto py-16 text-center space-y-4">
        <div className="text-4xl">⚠️</div>
        <h2 className="text-xl font-bold">Job Not Found</h2>
        <p className="text-text-muted text-sm">{error || "Could not retrieve details for this job."}</p>
        <Link
          href="/dashboard/jobs"
          className="inline-block px-5 py-2 bg-gradient-to-r from-accent to-cyan text-white text-sm font-medium rounded-lg"
        >
          ← Back to Jobs
        </Link>
      </div>
    );
  }

  const isRunning = job.status === "running" || job.status === "queued" || job.status === "pending";

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* ---- Header ---- */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/dashboard/jobs" className="text-xs text-text-muted hover:text-accent-light mb-2 inline-block">
            ← Back to Jobs
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{job.video_filename}</h1>
            <span
              className={`text-xs font-medium px-3 py-1 rounded-full border capitalize ${
                job.status === "completed"
                  ? "bg-emerald/10 text-emerald border-emerald/20"
                  : job.status === "failed"
                  ? "bg-rose/10 text-rose border-rose/20"
                  : job.status === "running"
                  ? "bg-cyan/10 text-cyan border-cyan/20"
                  : "bg-amber/10 text-amber border-amber/20"
              }`}
            >
              {job.status}
            </span>
          </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-text-muted">
            <span>Target: {job.pipeline_config?.target_resolution || "4K"}</span>
            <span>•</span>
            <span className="capitalize">Preset: {job.pipeline_config?.quality_preset || "balanced"}</span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${wsConnected ? "bg-emerald animate-pulse" : "bg-text-muted"}`} />
              {wsConnected ? "Live Updates" : "Polling"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isRunning && (
            <button
              onClick={handleCancel}
              className="px-4 py-2 border border-border rounded-lg text-sm text-text-secondary hover:border-rose/50 hover:text-rose transition-colors"
            >
              Cancel Job
            </button>
          )}

          {job.status === "completed" && job.download_url && (
            <a
              href={job.download_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2 bg-gradient-to-r from-accent via-indigo to-cyan text-white text-sm font-semibold rounded-lg hover:opacity-90 shadow-lg shadow-accent/20 transition-all"
            >
              Download 4K Output ⬇
            </a>
          )}
        </div>
      </div>

      {/* ---- Overall Progress ---- */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-sm font-medium">Overall Progress</span>
            {job.estimated_time_remaining_seconds != null && (
              <span className="ml-3 text-xs text-text-muted">
                ETA: ~{Math.ceil(job.estimated_time_remaining_seconds / 60)} min remaining
              </span>
            )}
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold gradient-text">{job.overall_progress.toFixed(1)}%</span>
          </div>
        </div>
        <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${
              job.status === "completed"
                ? "bg-emerald"
                : job.status === "failed"
                ? "bg-rose"
                : "bg-gradient-to-r from-accent via-cyan to-emerald shimmer"
            }`}
            style={{ width: `${job.overall_progress}%` }}
          />
        </div>
        {job.error_message && (
          <div className="mt-4 p-3 rounded-lg bg-rose/10 border border-rose/20 text-rose text-xs">
            ❌ Error in stage {job.error_stage}: {job.error_message}
          </div>
        )}
      </div>

      {/* ---- Pipeline Stages ---- */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-5">Pipeline Stages ({job.stages?.length || 0})</h2>
        <div className="space-y-1">
          {(job.stages || []).map((stage: StageProgress, i: number) => (
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
                  <span className="text-sm font-medium">{stage.stage_display_name || stage.stage}</span>
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

              {/* Progress Bar for running stage */}
              {stage.status === "running" && (
                <div className="w-24 flex items-center gap-2 shrink-0">
                  <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-accent to-cyan rounded-full shimmer"
                      style={{ width: `${stage.progress_percent}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono text-accent-light">{stage.progress_percent}%</span>
                </div>
              )}

              {/* Duration */}
              <span className="text-xs text-text-muted w-16 text-right shrink-0 hidden sm:block">
                {stage.duration_seconds ? `${stage.duration_seconds}s` : "—"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ---- Result Summary ---- */}
      {job.result && (
        <div className="glass-card p-6 border-emerald/30">
          <h2 className="font-semibold mb-4 text-emerald flex items-center gap-2">
            <span>🎉</span> Processing Complete
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-3 bg-bg-tertiary/40 rounded-xl">
              <div className="text-xs text-text-muted mb-1">Output Resolution</div>
              <div className="text-lg font-bold">
                {job.result.output_resolution_width}x{job.result.output_resolution_height}
              </div>
            </div>
            <div className="p-3 bg-bg-tertiary/40 rounded-xl">
              <div className="text-xs text-text-muted mb-1">Frames Processed</div>
              <div className="text-lg font-bold">{job.result.total_frames_processed}</div>
            </div>
            <div className="p-3 bg-bg-tertiary/40 rounded-xl">
              <div className="text-xs text-text-muted mb-1">Total Processing Time</div>
              <div className="text-lg font-bold">{job.result.total_processing_time_seconds.toFixed(1)}s</div>
            </div>
            <div className="p-3 bg-bg-tertiary/40 rounded-xl">
              <div className="text-xs text-text-muted mb-1">Output FPS</div>
              <div className="text-lg font-bold">{job.result.output_fps}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
