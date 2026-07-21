/* ChronoColor 4K AI — API Client */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}/api/v1${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

// ---- Videos ----

export async function uploadVideo(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const url = `${API_BASE}/api/v1/videos/upload`;
  const res = await fetch(url, { method: "POST", body: formData });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function listVideos(page = 1, pageSize = 20) {
  return request<{
    videos: import("@/types").Video[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>(`/videos?page=${page}&page_size=${pageSize}`);
}

export async function getVideo(id: string) {
  return request<import("@/types").Video>(`/videos/${id}`);
}

export async function deleteVideo(id: string) {
  await fetch(`${API_BASE}/api/v1/videos/${id}`, { method: "DELETE" });
}

// ---- Jobs ----

export async function createJob(videoId: string, config?: Partial<import("@/types").PipelineConfig>) {
  return request<import("@/types").Job>("/jobs", {
    method: "POST",
    body: JSON.stringify({ video_id: videoId, pipeline_config: config || {} }),
  });
}

export async function listJobs(page = 1, pageSize = 20, status?: string) {
  let url = `/jobs?page=${page}&page_size=${pageSize}`;
  if (status) url += `&status=${status}`;
  return request<{
    jobs: import("@/types").Job[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>(url);
}

export async function getJob(id: string) {
  return request<import("@/types").Job>(`/jobs/${id}`);
}

export async function cancelJob(id: string) {
  return request(`/jobs/${id}/cancel`, { method: "POST" });
}

export async function getPresets() {
  return request<import("@/types").PipelinePreset[]>("/jobs/presets");
}

// ---- Health ----

export async function healthCheck() {
  return request<{ status: string; checks: Record<string, string> }>("/health");
}

// ---- WebSocket ----

export function connectJobWebSocket(jobId: string): WebSocket {
  const wsBase = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
  return new WebSocket(`${wsBase}/api/v1/ws/${jobId}`);
}
