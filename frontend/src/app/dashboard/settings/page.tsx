"use client";

export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-sm text-text-muted">Configure your ChronoColor 4K AI preferences.</p>
      </div>

      {/* Default Pipeline Settings */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-4">Default Pipeline</h2>
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

      {/* GPU Settings */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-4">GPU & Performance</h2>
        <div className="space-y-4">
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
          <div className="flex items-center justify-between py-2">
            <div>
              <div className="text-sm font-medium">Max Concurrent Workers</div>
              <div className="text-xs text-text-muted">GPU workers for parallel processing</div>
            </div>
            <input
              type="number"
              defaultValue="2"
              min="1"
              max="8"
              className="w-20 bg-bg-tertiary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary text-center outline-none focus:border-accent/50"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button className="px-6 py-2.5 bg-gradient-to-r from-accent to-cyan text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity">
          Save Settings
        </button>
      </div>
    </div>
  );
}
