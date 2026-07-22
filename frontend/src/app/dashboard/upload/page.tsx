"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { uploadVideo, createJob, getPresets } from "@/lib/api";
import type { PipelinePreset } from "@/types";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState("balanced");
  const [presets, setPresets] = useState<PipelinePreset[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPresets()
      .then((data) => setPresets(data))
      .catch((err) => console.error("Failed to fetch presets:", err));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    setError(null);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith("video/")) {
      setFile(droppedFile);
    } else {
      setError("Please drop a valid video file.");
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      setUploadStatus("Uploading video to server...");
      const uploadRes = await uploadVideo(file);

      setUploadStatus("Initializing AI Pipeline job...");
      const jobRes = await createJob(uploadRes.id, {
        quality_preset: selectedPreset,
      });

      setUploadStatus("Redirecting to job status...");
      router.push(`/dashboard/jobs/${jobRes.id}`);
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(err.message || "Failed to upload or start processing job.");
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* ---- Page Header ---- */}
      <div>
        <h1 className="text-2xl font-bold mb-2">Upload Video</h1>
        <p className="text-text-secondary text-sm">
          Upload a black & white video to transform it into a cinematic 4K color masterpiece.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose/10 border border-rose/20 text-rose text-sm flex items-center justify-between">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)} className="text-xs hover:underline">Dismiss</button>
        </div>
      )}

      {/* ---- Drop Zone ---- */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
          dragActive
            ? "border-accent bg-accent/5 scale-[1.01]"
            : file
            ? "border-emerald/40 bg-emerald/5"
            : "border-border hover:border-accent/40 hover:bg-accent/5"
        }`}
        onClick={() => !file && !uploading && document.getElementById("file-input")?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />

        {!file ? (
          <>
            <div className="w-20 h-20 mx-auto rounded-2xl bg-bg-tertiary flex items-center justify-center text-4xl mb-6 animate-float">
              📹
            </div>
            <h3 className="text-lg font-semibold mb-2">
              {dragActive ? "Drop your video here" : "Drag & drop your video"}
            </h3>
            <p className="text-sm text-text-muted mb-4">
              or click to browse files
            </p>
            <div className="flex items-center justify-center gap-4 text-xs text-text-muted">
              <span className="px-2 py-1 bg-bg-tertiary rounded">MP4</span>
              <span className="px-2 py-1 bg-bg-tertiary rounded">AVI</span>
              <span className="px-2 py-1 bg-bg-tertiary rounded">MOV</span>
              <span className="px-2 py-1 bg-bg-tertiary rounded">MKV</span>
              <span className="px-2 py-1 bg-bg-tertiary rounded">WebM</span>
            </div>
            <p className="text-[11px] text-text-muted mt-3">Max 5 GB • Up to 10 min</p>
          </>
        ) : (
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-xl bg-emerald/10 flex items-center justify-center text-3xl shrink-0">
              ✅
            </div>
            <div className="text-left flex-1">
              <div className="font-semibold text-lg">{file.name}</div>
              <div className="text-sm text-text-muted mt-0.5">
                {formatSize(file.size)} • {file.type || "video/*"}
              </div>
            </div>
            {!uploading && (
              <button
                onClick={(e) => { e.stopPropagation(); setFile(null); }}
                className="p-2 rounded-lg hover:bg-bg-tertiary text-text-muted hover:text-rose transition-colors"
              >
                ✕
              </button>
            )}
          </div>
        )}
      </div>

      {/* ---- Quality Presets ---- */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Quality Preset</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(presets.length > 0
            ? presets
            : [
                { name: "fast", display_name: "Fast", description: "Essential stages only. 1080p output.", active_stages: 7, target_resolution: "1080p" },
                { name: "balanced", display_name: "Balanced", description: "Full pipeline. 4K output. Recommended.", active_stages: 16, target_resolution: "4K" },
                { name: "maximum", display_name: "Maximum Quality", description: "Premium models. Highest quality 4K.", active_stages: 16, target_resolution: "4K" },
              ]
          ).map((preset) => (
            <button
              key={preset.name}
              disabled={uploading}
              onClick={() => setSelectedPreset(preset.name)}
              className={`glass-card p-5 text-left transition-all ${
                selectedPreset === preset.name
                  ? "border-accent/60 shadow-lg shadow-accent/10"
                  : "hover:border-border-hover"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-lg font-semibold">
                  {preset.name === "fast" ? "⚡ " : preset.name === "balanced" ? "⚖️ " : "💎 "}
                  {preset.display_name}
                </span>
                {preset.name === "balanced" && (
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-accent/15 text-accent-light border border-accent/20">
                    Recommended
                  </span>
                )}
              </div>
              <p className="text-xs text-text-muted mb-4">{preset.description}</p>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="w-5 h-5 rounded bg-gradient-to-br from-accent to-cyan flex items-center justify-center text-[10px] text-white font-bold">
                    {preset.active_stages}
                  </div>
                  <span className="text-text-muted">stages</span>
                </div>
                <div className="flex items-center gap-1.5 text-text-muted">
                  📐 {preset.target_resolution}
                </div>
              </div>

              {selectedPreset === preset.name && (
                <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-accent to-cyan" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* ---- Upload Button ---- */}
      <div className="flex items-center justify-between pt-4 border-t border-border">
        <div className="text-sm text-text-muted">
          {uploading
            ? uploadStatus
            : file
            ? `Ready to upload & process ${file.name} with ${selectedPreset} preset`
            : "Select a video file to continue"}
        </div>
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`px-8 py-3 rounded-xl font-semibold text-white transition-all ${
            file && !uploading
              ? "bg-gradient-to-r from-accent to-cyan hover:opacity-90 shadow-lg shadow-accent/20 cursor-pointer"
              : "bg-bg-tertiary text-text-muted cursor-not-allowed"
          }`}
        >
          {uploading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Processing...
            </span>
          ) : (
            "Start Processing →"
          )}
        </button>
      </div>
    </div>
  );
}
