"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: "📊" },
  { href: "/dashboard/upload", label: "Upload", icon: "📤" },
  { href: "/dashboard/jobs", label: "Jobs", icon: "⚡" },
  { href: "/dashboard/settings", label: "Settings", icon: "⚙️" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen">
      {/* ---- Sidebar ---- */}
      <aside className="w-64 border-r border-border bg-bg-secondary/50 backdrop-blur-sm flex flex-col shrink-0">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-border">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-cyan flex items-center justify-center text-sm font-bold text-white">
              CC
            </div>
            <div>
              <div className="font-semibold text-sm leading-tight">ChronoColor</div>
              <div className="text-[10px] text-accent-light font-medium">4K AI</div>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-accent/15 text-accent-light border border-accent/20"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50"
                }`}
              >
                <span className="text-base">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* GPU Status */}
        <div className="p-4 border-t border-border">
          <div className="glass-card p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-text-muted">GPU Status</span>
              <span className="w-2 h-2 rounded-full bg-emerald animate-pulse" />
            </div>
            <div className="text-xs text-text-secondary">
              <div className="flex justify-between mb-1">
                <span>VRAM</span>
                <span className="text-text-primary">12.4 / 24 GB</span>
              </div>
              <div className="h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-accent to-cyan rounded-full transition-all"
                  style={{ width: "52%" }}
                />
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ---- Main Content ---- */}
      <main className="flex-1 overflow-auto">
        {/* Top Bar */}
        <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-bg-primary/80 backdrop-blur-sm sticky top-0 z-40">
          <div className="text-sm text-text-muted">
            {pathname === "/dashboard" && "Dashboard Overview"}
            {pathname === "/dashboard/upload" && "Upload Video"}
            {pathname.startsWith("/dashboard/jobs") && "Processing Jobs"}
            {pathname === "/dashboard/settings" && "Settings"}
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard/upload"
              className="px-4 py-1.5 bg-gradient-to-r from-accent to-cyan text-white text-xs font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              + New Upload
            </Link>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
