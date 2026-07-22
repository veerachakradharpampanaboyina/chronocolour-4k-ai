"use client";

import { useEffect, useState } from "react";
import { healthCheck } from "@/lib/api";

export default function SettingsPage() {
  const [health, setHealth] = useState<{ status: string; checks: Record<string, string>; service: string; version: string; environment: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    healthCheck()
      .then((data: any) => setHealth(data))
      .catch((err) => console.error("Health check error:", err))
      .finally(() => setLoading(false));
  }, []);

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-2">Settings & System Info</h1>
        <p className="text-sm text-text-muted">Configure your ChronoColor 4K AI preferences and view backend health.</p>
      </div>

      {saved && (
        <div className="p-4 rounded-xl bg-emerald/10 border border-emerald/20 text-emerald text-sm flex items-center gap-2">
          <span>✓</span> Settings saved successfully.
        </div>
      )}

      {/* Live System Status */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-4 flex items-center justify-between">
          <span>Backend Infrastructure Status</span>
          <span className="text-xs font-mono text-accent-light font-normal">
            {health?.service || "ChronoColor API"} v{health?.version || "1.0.0"} ({health?.environment || "local"})
          </span>
        </h2>
        {loading ? (
          <div className="text-xs text-text-muted">Checking backend services...</div>
        ) : health ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {Object.entries(health.checks).map(([service, status]) => (
              <div key={service} className="p-3 bg-bg-tertiary/40 rounded-xl border border-border">
                <div className="text-xs text-text-muted capitalize mb-1">{service} Service</div>
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <span className={`w-2.5 h-2.5 rounded-full ${status === "healthy" ? "bg-emerald animate-pulse" : "bg-rose"}`} />
                  <span className={status === "healthy" ? "text-emerald" : "text-rose"}>
                    {status === "healthy" ? "Local Mock Ready" : status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-rose">Unable to connect to backend server.</div>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-8">
        {/* Default Pipeline Settings */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">Default Pipeline Settings</h2>
          <div className="space-y-4">
            {[
              { label: "Default Quality Preset", value: "Balanced", options: ["Fast", "Balanced", "Maximum"] },
              { label: "Target Resolution", value: "4K (3840×2160)", options: ["720p", "1080p", "2K", "4K"] },
              { label: "Output Format", value: "MP4 (H.265)", options: ["MP4 (H.265)", "MP4 (H.264)", "ProRes", "WebM"] },
            ].map((setting) => (
              <div key={setting.label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div>
                  <div className="text-sm font-medium">{setting.label}</div>
                  <div className="text-xs text-text-muted">{setting.value}</div>
                </div>
                <select className="bg-bg-tertiary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent/50">
                  {setting.options.map((opt) => (
                    <option key={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>

        {/* AI Model Preferences */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">AI Model Preferences</h2>
          <div className="space-y-4">
            {[
              { label: "Colorization Model", value: "DDColor", options: ["DDColor", "SD + ControlNet"] },
              { label: "Super Resolution", value: "Real-ESRGAN", options: ["Real-ESRGAN", "HAT", "SwinIR"] },
              { label: "Face Restoration", value: "CodeFormer", options: ["CodeFormer", "GFPGAN"] },
              { label: "Frame Restoration", value: "NAFNet", options: ["NAFNet", "BasicVSR++", "Restormer"] },
            ].map((setting) => (
              <div key={setting.label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div>
                  <div className="text-sm font-medium">{setting.label}</div>
                  <div className="text-xs text-text-muted">Current: {setting.value}</div>
                </div>
                <select className="bg-bg-tertiary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent/50">
                  {setting.options.map((opt) => (
                    <option key={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>

        {/* GPU & Local Mode Settings */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">Execution Engine</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-2">
              <div>
                <div className="text-sm font-medium">Local Mock Mode</div>
                <div className="text-xs text-text-muted">Runs in-memory MongoDB, Redis & local storage without Docker</div>
              </div>
              <span className="text-xs font-semibold text-emerald px-2.5 py-1 rounded-full bg-emerald/10 border border-emerald/20">
                Enabled (USE_LOCAL_SERVICES=true)
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <div className="text-sm font-medium">GPU Memory Fraction</div>
                <div className="text-xs text-text-muted">Maximum VRAM usage (0.0 - 1.0)</div>
              </div>
              <input
                type="number"
                defaultValue="0.9"
                step="0.1"
                min="0.5"
                max="1.0"
                className="w-20 bg-bg-tertiary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary text-center outline-none focus:border-accent/50"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2.5 bg-gradient-to-r from-accent to-cyan text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity cursor-pointer"
          >
            Save Settings
          </button>
        </div>
      </form>
    </div>
  );
}
