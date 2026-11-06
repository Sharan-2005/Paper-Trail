import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, FilePlus, FileSearch, GitBranch, Eye, 
  BookOpen, FileText, History, Settings, ChevronLeft,
  ChevronRight, Scan, AlertTriangle, Shield
} from 'lucide-react';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: FilePlus, label: 'New Investigation', path: '/investigation/new' },
  { icon: FileSearch, label: 'Document Analysis', path: '/investigation/new' },
  { icon: GitBranch, label: 'Cross-Document Intelligence', path: '/cross-document' },
  { icon: Eye, label: 'Visual Forensics', path: '/visual-forensics' },
  { icon: BookOpen, label: 'Evidence Explorer', path: '/evidence' },
  { icon: FileText, label: 'Investigation Reports', path: '/reports' },
  { icon: History, label: 'Investigation History', path: '/history' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className={clsx(
        'flex flex-col border-r border-white/8 transition-all duration-300 relative z-10',
        collapsed ? 'w-16' : 'w-64',
      )}
        style={{ background: 'linear-gradient(180deg, #0d1829 0%, #101C2B 100%)' }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-white/8">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #45D6E8, #2AB5C8)' }}>
            <Scan className="w-5 h-5 text-navy-200" />
          </div>
          {!collapsed && (
            <div>
              <div className="text-white font-bold text-base leading-tight">PaperTrail</div>
              <div className="text-cyan-primary text-xs font-medium">Follow the Evidence</div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
              (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
            
            return (
              <button
                key={item.path + item.label}
                onClick={() => navigate(item.path)}
                className={clsx('sidebar-item w-full text-left', { active: isActive })}
                title={collapsed ? item.label : undefined}
              >
                <Icon className="w-4.5 h-4.5 flex-shrink-0" size={18} />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {/* System status */}
        {!collapsed && (
          <div className="p-4 border-t border-white/8">
            <div className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wider">System Status</div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              Backend Connected
            </div>
          </div>
        )}

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-20 w-6 h-6 rounded-full border border-white/15 
                     bg-navy-200 flex items-center justify-center hover:border-cyan-primary/50 
                     transition-all duration-200"
        >
          {collapsed 
            ? <ChevronRight className="w-3 h-3 text-slate-400" /> 
            : <ChevronLeft className="w-3 h-3 text-slate-400" />
          }
        </button>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="page-transition">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

