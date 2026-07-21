/* ChronoColor 4K AI — TypeScript Types */

export interface Video {
  id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  status: VideoStatus;
  created_at: string;
  updated_at: string;
  duration_seconds?: number;
  resolution?: string;
  is_grayscale?: boolean;
  content_type?: string;
  analysis?: VideoAnalysis;
  download_url?: string;
}

export type VideoStatus =
  | "uploading"
  | "uploaded"
  | "analyzing"
  | "analyzed"
  | "processing"
  | "completed"
  | "failed"
  | "deleted";

export interface VideoAnalysis {
  resolution_width: number;
  resolution_height: number;
  fps: number;
  total_frames: number;
  duration_seconds: number;
  codec: string;
  bitrate_kbps: number;
  file_size_bytes: number;
  noise_level: number;
  blur_level: number;
  damage_level: number;
  compression_artifact_level: number;
  scene_change_count: number;
  is_grayscale: boolean;
  has_audio: boolean;
}

export interface Job {
  id: string;
  video_id: string;
  video_filename: string;
  status: JobStatus;
  overall_progress: number;
  current_stage?: string;
  current_stage_display_name?: string;
  pipeline_config: PipelineConfig;
  stages: StageProgress[];
  result?: JobResult;
  error_message?: string;
  error_stage?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  estimated_time_remaining_seconds?: number;
  download_url?: string;
}

export type JobStatus =
  | "pending"
  | "queued"
  | "running"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled";

export interface StageProgress {
  stage: string;
  stage_display_name: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  progress_percent: number;
  message: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds: number;
  error?: string;
}

export interface PipelineConfig {
  quality_preset: string;
  enable_restoration: boolean;
  enable_super_resolution: boolean;
  enable_face_restoration: boolean;
  enable_scene_understanding: boolean;
  enable_object_detection: boolean;
  enable_object_tracking: boolean;
  enable_segmentation: boolean;
  enable_colorization: boolean;
  enable_temporal_memory: boolean;
  enable_optical_flow: boolean;
  enable_flicker_correction: boolean;
  enable_hdr_enhancement: boolean;
  enable_quality_assessment: boolean;
  target_resolution: string;
  output_format: string;
}

export interface JobResult {
  output_storage_bucket: string;
  output_storage_key: string;
  output_file_size_bytes: number;
  output_resolution_width: number;
  output_resolution_height: number;
  output_duration_seconds: number;
  output_fps: number;
  total_frames_processed: number;
  total_processing_time_seconds: number;
}

export interface PipelinePreset {
  name: string;
  display_name: string;
  description: string;
  estimated_time_multiplier: number;
  active_stages: number;
  target_resolution: string;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: T[];
}

export interface ProgressMessage {
  type: "connected" | "progress" | "heartbeat" | "completed";
  job_id: string;
  stage?: string;
  status?: string;
  progress?: number;
  message?: string;
  final_status?: string;
  timestamp?: string;
}
