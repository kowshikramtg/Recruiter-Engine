"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  BarChart3,
  Target,
  Cpu,
  Radar,
  Clock,
  Settings,
  Zap,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/jobs", label: "Role DNA", icon: Briefcase },
  { href: "/analysis", label: "AI Pipeline", icon: Cpu },
  { href: "/compare", label: "Compare", icon: Target },
  { href: "/time-machine", label: "Time Machine", icon: Clock },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 flex flex-col"
      style={{ background: "var(--surface)", borderRight: "1px solid var(--border-subtle)" }}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b" style={{ borderColor: "var(--border-subtle)" }}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: "linear-gradient(135deg, #6366F1, #818CF8)" }}>
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-white">Hiring Intelligence</p>
          <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>AI Recruiter Engine</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname?.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group ${
                isActive
                  ? "text-white"
                  : "hover:bg-white/5"
              }`}
              style={isActive ? {
                background: "rgba(99, 102, 241, 0.15)",
                color: "var(--primary-light)",
                border: "1px solid rgba(99, 102, 241, 0.2)",
              } : { color: "var(--text-secondary)" }}
            >
              <Icon
                size={16}
                style={{ color: isActive ? "var(--primary-light)" : "var(--text-muted)" }}
                className="group-hover:scale-110 transition-transform"
              />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
        <Link
          href="/settings"
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
            pathname === "/settings" ? "" : "hover:bg-white/5"
          }`}
          style={{ color: "var(--text-secondary)" }}
        >
          <Settings size={16} style={{ color: "var(--text-muted)" }} />
          Settings
        </Link>
        <div className="mt-3 px-3">
          <div className="text-[10px] font-medium px-2 py-1 rounded-full text-center w-fit"
            style={{ background: "rgba(99, 102, 241, 0.15)", color: "var(--primary-light)" }}>
            MVP v1.0
          </div>
        </div>
      </div>
    </aside>
  );
}
