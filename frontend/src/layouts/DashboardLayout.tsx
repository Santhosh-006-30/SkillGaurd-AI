import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  Shield, LayoutDashboard, Building2, AlertTriangle,
  BarChart3, FileText, CheckCircle2, Server, EyeOff,
  LogOut, User as UserIcon, Radio, Menu, X
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', label: 'Monitoring Dashboard', icon: LayoutDashboard },
    { to: '/centres', label: 'Training Centres', icon: Building2 },
    { to: '/alerts', label: 'Compliance Alerts', icon: AlertTriangle },
    { to: '/analytics', label: 'Analytics & Risk', icon: BarChart3 },
    { to: '/evaluation', label: 'AI Model Evaluation', icon: CheckCircle2 },
    { to: '/reports', label: 'Inspection Reports', icon: FileText },
    { to: '/privacy', label: 'Privacy Framework', icon: EyeOff },
    { to: '/system', label: 'System Health & Node', icon: Server },
  ];

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="sticky top-0 z-40 border-b border-gray-800 bg-[#111827]/90 backdrop-blur px-4 lg:px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-1.5 text-slate-400 hover:text-white"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <NavLink to="/dashboard" className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-wide text-white">SKILLGUARD AI</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 bg-blue-900/60 text-blue-300 border border-blue-700/50 rounded">
                  SIH 26245
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                MSDE Training Centre Compliance & Infrastructure Oversight
              </p>
            </div>
          </NavLink>
        </div>

        {/* Top Badges & User Session */}
        <div className="flex items-center space-x-3 sm:space-x-4 text-xs font-mono">
          <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>SOC REAL-TIME</span>
          </div>

          <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
            <EyeOff className="w-3.5 h-3.5 text-blue-400" />
            <span>ZERO FACIAL RECOGNITION</span>
          </div>

          <div className="flex items-center space-x-2 pl-2 border-l border-gray-800">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#1c273c] text-slate-200 border border-gray-700">
              <UserIcon className="w-3.5 h-3.5 text-blue-400" />
              <span className="font-medium">{user?.username}</span>
              <span className="text-[10px] text-blue-300 px-1 py-0.5 bg-blue-900/60 rounded">
                {user?.role}
              </span>
            </div>

            <button
              onClick={handleLogout}
              className="p-1.5 rounded hover:bg-rose-900/30 text-slate-400 hover:text-rose-300 transition-colors"
              title="Logout session"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main App Container with Sidebar & Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-[#0f172a] border-r border-gray-800 flex flex-col justify-between transition-transform transform ${
            mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          } pt-16 lg:pt-0`}
        >
          <div className="p-4 space-y-1">
            <div className="px-3 py-2 text-[10px] uppercase font-mono tracking-wider text-slate-400">
              Navigation
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold'
                        : 'text-slate-300 hover:bg-[#162136] hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>

          {/* Sidebar Footer info */}
          <div className="p-4 border-t border-gray-800 bg-[#0c1222] text-[11px] font-mono text-slate-400 space-y-1">
            <div className="flex items-center justify-between">
              <span>Environment:</span>
              <span className="text-emerald-400">LOCAL MVP</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Version:</span>
              <span className="text-slate-300">v1.0.0</span>
            </div>
            <div className="text-[10px] text-slate-500 pt-1">
              Simulated Demo Data Active
            </div>
          </div>
        </aside>

        {/* Content View Area */}
        <main className="flex-1 overflow-y-auto bg-[#0B0F19] p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
