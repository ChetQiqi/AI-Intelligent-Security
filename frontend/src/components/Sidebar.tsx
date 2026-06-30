/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import {
  LayoutDashboard,
  Users,
  Frame,
  Video,
  Terminal,
  ShieldAlert,
  HeartPulse,
  Radio,
  LogOut,
  Shield,
  Wand2,
  ChartNoAxesCombined,
} from 'lucide-react';
import { Language, LOCALES } from '../locales';
import { useAuth } from '../hooks/useAuth';
import type { User } from '../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onEmergencyLockdown: () => void;
  isLockedDown: boolean;
  language: Language;
  user: User | null;
  appearance?: 'research' | 'dark';
}

export default function Sidebar({
  activeTab,
  setActiveTab,
  onEmergencyLockdown,
  isLockedDown,
  language,
  user,
  appearance = 'dark',
}: SidebarProps) {
  const { logout } = useAuth();
  const t = LOCALES[language];
  const isDeveloper = user?.role === 'developer' || user?.role === 'admin';
  const isAdmin = user?.role === 'admin';
  const isResearch = appearance === 'research';

  const allMenuItems = [
    { id: 'dashboard', label: t.sidebar.dashboard, icon: LayoutDashboard, roles: ['viewer', 'developer', 'admin'] },
    { id: 'people', label: t.sidebar.people, icon: Users, roles: ['viewer', 'developer', 'admin'] },
    { id: 'portrait', label: t.sidebar.portrait, icon: Wand2, roles: ['viewer', 'developer', 'admin'] },
    { id: 'recognition', label: t.sidebar.recognition, icon: Frame, roles: ['viewer', 'developer', 'admin'] },
    { id: 'video', label: t.sidebar.video, icon: Video, roles: ['viewer', 'developer', 'admin'] },
    {
      id: 'security',
      label: language === 'zh' ? '安防驾驶舱' : 'Security Cockpit',
      icon: ChartNoAxesCombined,
      roles: ['viewer', 'developer', 'admin'],
    },
    { id: 'developer', label: t.sidebar.developer, icon: Terminal, roles: ['developer', 'admin'] },
    { id: 'admin', label: isAdmin ? 'Admin Panel' : '', icon: Shield, roles: ['admin'] },
  ];

  const menuItems = allMenuItems.filter(
    (item) => user && item.roles.includes(user.role) && item.label
  );

  return (
    <aside
      className={`w-20 lg:w-64 border-r flex flex-col justify-between h-screen shrink-0 font-sans select-none transition-colors duration-200 ${
        isResearch
          ? 'research-shell-sidebar border-slate-200 bg-white text-slate-600'
          : 'border-[#262b35] bg-[#181c24] text-[#94a3b8]'
      }`}
    >
      {/* Upper Brand Section */}
      <div>
        <div
          className={`px-4 py-6 lg:p-6 border-b ${
            isResearch
              ? 'border-[#1d3659] bg-[#10233f]'
              : 'border-[#262b35] bg-[#12161f]'
          }`}
        >
          <h1 className="text-xl font-bold tracking-wider text-white flex items-center justify-center lg:justify-start gap-2 font-mono">
            <span
              className={`font-extrabold uppercase ${
                isResearch ? 'text-blue-300' : 'text-cyan-400 animate-pulse'
              }`}
            >
              E-
            </span>
            <span className="hidden lg:inline">RECOGNITION</span>
          </h1>
          <p
            className={`hidden lg:block text-xs mt-1 uppercase tracking-widest font-mono truncate ${
              isResearch ? 'text-blue-200/70' : 'text-slate-500'
            }`}
          >
            {t.sidebar.appName}
          </p>
        </div>

        {/* Navigation Tabs */}
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => !isLockedDown && setActiveTab(item.id)}
                disabled={isLockedDown}
                aria-label={item.label}
                title={item.label}
                className={`w-full flex items-center justify-center lg:justify-start gap-3 px-3 lg:px-4 py-3 text-sm font-medium rounded-sm transition-all duration-200 ${
                  isActive
                    ? isResearch
                      ? 'bg-blue-50 text-blue-800 border-l-2 border-blue-600 font-semibold'
                      : 'bg-[#1e293b]/80 text-[#38bdf8] border-l-2 border-[#06b6d4] font-semibold'
                    : isLockedDown
                      ? 'opacity-40 cursor-not-allowed'
                      : isResearch
                        ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
                        : 'hover:bg-[#1a202c] hover:text-white text-slate-400'
                }`}
              >
                <Icon
                  className={`w-4 h-4 ${
                    isActive
                      ? isResearch
                        ? 'text-blue-700'
                        : 'text-[#22d3ee]'
                      : 'text-slate-500'
                  }`}
                />
                <span className="hidden lg:inline">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Safety & Status Footing */}
      <div
        className={`p-4 border-t space-y-4 ${
          isResearch
            ? 'border-slate-200 bg-slate-50'
            : 'border-[#262b35] bg-[#12161f]/80'
        }`}
      >
        {/* User info */}
        {user && (
          <div className="flex items-center gap-2 px-1">
            <div className="w-7 h-7 rounded-sm bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-[10px] font-bold text-cyan-400 uppercase">
              {user.username.charAt(0)}
            </div>
            <div className="hidden min-w-0 flex-1 lg:block">
              <p
                className={`text-[11px] font-semibold truncate ${
                  isResearch ? 'text-slate-700' : 'text-slate-300'
                }`}
              >
                {user.username}
              </p>
              <p
                className={`text-[9px] font-mono uppercase tracking-wider ${
                  isResearch ? 'text-blue-700' : 'text-cyan-400'
                }`}
              >
                {user.role}
              </p>
            </div>
          </div>
        )}

        {/* Emergency Button */}
        <button
          onClick={onEmergencyLockdown}
          aria-label={
            isLockedDown
              ? language === 'zh'
                ? '恢复系统授权'
                : 'Authorize Re-entry'
              : t.sidebar.emergencyLockdown
          }
          className={`w-full py-3.5 px-4 rounded-sm font-semibold tracking-wider flex items-center justify-center gap-2 text-xs uppercase transition-all duration-300 ${
            isLockedDown
              ? 'bg-emerald-500 hover:bg-emerald-600 text-white animate-pulse shadow-lg shadow-emerald-500/20'
              : 'bg-red-950 hover:bg-red-800 border border-red-500/30 hover:border-red-500 text-red-200 hover:text-red-100 hover:scale-[1.02] active:scale-[0.98]'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span className="hidden lg:inline">
            {isLockedDown
              ? language === 'zh'
                ? '恢复系统授权'
                : 'Authorize Re-entry'
              : t.sidebar.emergencyLockdown}
          </span>
        </button>

        {/* Logout */}
        <button
          onClick={logout}
          aria-label={language === 'zh' ? '登出系统' : 'Logout'}
          className={`w-full py-2.5 px-4 rounded-sm font-semibold tracking-wider flex items-center justify-center gap-2 text-xs uppercase transition-all ${
            isResearch
              ? 'text-slate-500 hover:bg-red-50 hover:text-red-700'
              : 'text-slate-500 hover:text-red-400 hover:bg-red-950/30'
          }`}
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden lg:inline">{language === 'zh' ? '登出系统' : 'Logout'}</span>
        </button>

        {/* Status indicators */}
        <div className="hidden space-y-2 pt-1 font-mono text-[11px] text-slate-500 lg:block">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <HeartPulse className="w-3.5 h-3.5 text-emerald-500" />
              <span>{language === 'zh' ? '系统生存雷达' : 'System Health'}</span>
            </div>
            <span className="text-emerald-400 font-semibold uppercase">
              {language === 'zh' ? '最优化' : 'Nominal'}
            </span>
          </div>

          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <Radio className="w-3.5 h-3.5 text-[#38bdf8] animate-pulse" />
              <span>{language === 'zh' ? '密级物理联锁' : 'Network Status'}</span>
            </div>
            <span className="text-[#38bdf8] uppercase">{language === 'zh' ? '特级安全' : 'Secure'}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
