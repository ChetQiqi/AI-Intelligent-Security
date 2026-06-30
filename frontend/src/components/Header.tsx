/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Search, Bell, Settings } from 'lucide-react';
import { Language, LOCALES } from '../locales';
import type { User } from '../types';

interface HeaderProps {
  title: string;
  searchPlaceholder?: string;
  onSearchChange?: (val: string) => void;
  searchValue?: string;
  toggleApiSimulator?: () => void;
  apiBadgeCount?: number;
  language: Language;
  onChangeLanguage: (lang: Language) => void;
  user?: User | null;
  appearance?: 'research' | 'dark';
}

export default function Header({
  title,
  searchPlaceholder = 'Global search entities...',
  onSearchChange,
  searchValue = '',
  toggleApiSimulator,
  apiBadgeCount = 32,
  language,
  onChangeLanguage,
  user,
  appearance = 'dark',
}: HeaderProps) {
  const t = LOCALES[language];
  const isResearch = appearance === 'research';

  // Generate a deterministic color from username for the avatar
  const avatarColor = user
    ? `hsl(${user.username.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360}, 60%, 50%)`
    : '#ffaa00';

  return (
    <header
      className={`h-16 border-b px-3 sm:px-4 lg:px-6 flex items-center justify-between gap-3 font-sans shrink-0 select-none transition-colors duration-200 ${
        isResearch
          ? 'research-shell-header border-slate-200 bg-white text-slate-700'
          : 'border-[#262b35] bg-[#11141e] text-slate-300'
      }`}
    >
      {/* Title / Section Heading */}
      <div className="flex items-center gap-3">
        <h2
          className={`max-w-[180px] truncate text-xs lg:max-w-none lg:text-sm font-semibold font-mono flex items-center gap-2 ${
            isResearch
              ? 'tracking-wide text-slate-600'
              : 'tracking-widest text-[#94a3b8] uppercase'
          }`}
        >
          <span
            className={`inline-block w-2 h-2 rounded-full ${
              isResearch ? 'bg-emerald-500' : 'bg-cyan-400 animate-ping'
            }`}
          />
          {title}
        </h2>
      </div>

      {/* Global Query Search Input */}
      <div className="relative hidden w-72 xl:block 2xl:w-96">
        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500">
          <Search className="w-4 h-4" />
        </span>
        <input
          type="text"
          value={searchValue}
          onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
          placeholder={searchPlaceholder}
          className={`w-full border pl-9 pr-4 py-2 text-xs outline-none transition-all font-sans ${
            isResearch
              ? 'rounded-lg border-slate-200 bg-slate-50 text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
              : 'rounded-sm border-[#262b35] bg-[#181d26] text-slate-200 focus:border-[#0891b2] focus:ring-1 focus:ring-cyan-900'
          }`}
        />
      </div>

      {/* Control Actions & Operator Bio */}
      <div className="flex items-center gap-2 lg:gap-4">
        {/* Language Selector Pill */}
        <div
          className={`flex p-0.5 border mr-1 ${
            isResearch
              ? 'rounded-lg border-slate-200 bg-slate-100'
              : 'rounded-sm border-[#262b35] bg-[#1a202c]'
          }`}
        >
          <button
            onClick={() => onChangeLanguage('en')}
            className={`px-2 py-1 text-[10px] font-mono leading-none rounded-md font-bold transition-all cursor-pointer ${
              language === 'en'
                ? isResearch
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'bg-cyan-500 text-slate-950 shadow-sm'
                : isResearch
                  ? 'text-slate-500 hover:text-slate-900'
                  : 'text-slate-400 hover:text-white'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => onChangeLanguage('zh')}
            className={`px-2 py-1 text-[10px] font-mono leading-none rounded-md font-bold transition-all cursor-pointer ${
              language === 'zh'
                ? isResearch
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'bg-cyan-500 text-slate-950 shadow-sm'
                : isResearch
                  ? 'text-slate-500 hover:text-slate-900'
                  : 'text-slate-400 hover:text-white'
            }`}
          >
            中文
          </button>
        </div>

        {/* Toggle API simulated catalog panel */}
        <button
          onClick={toggleApiSimulator}
          title="Open Backend API Inspector"
          className={`hidden lg:flex items-center gap-1.5 px-3 py-1.5 border text-xs font-mono transition-all cursor-pointer select-none ${
            isResearch
              ? 'rounded-lg border-slate-200 bg-white text-blue-700 hover:border-blue-300 hover:bg-blue-50'
              : 'rounded-sm border-[#334155]/60 bg-[#1e293b] text-cyan-400 hover:bg-[#334155] hover:text-white'
          }`}
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
          </span>
          <span>
            {t.header.apiSimulator} ({apiBadgeCount})
          </span>
        </button>

        {/* Notifications Icon */}
        <button
          aria-label={language === 'zh' ? '通知' : 'Notifications'}
          className={`relative p-2 rounded-full transition-colors cursor-pointer ${
            isResearch
              ? 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
              : 'text-slate-400 hover:bg-[#1a202c] hover:text-white'
          }`}
        >
          <Bell className="w-4 h-4" />
          <span
            className={`absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border ${
              isResearch ? 'border-white' : 'border-[#11141e]'
            }`}
          />
        </button>

        {/* Settings Icon */}
        <button
          aria-label={language === 'zh' ? '设置' : 'Settings'}
          className={`hidden sm:block p-2 rounded-full transition-colors cursor-pointer ${
            isResearch
              ? 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
              : 'text-slate-400 hover:bg-[#1a202c] hover:text-white'
          }`}
        >
          <Settings className="w-4 h-4" />
        </button>

        {/* Operator Profile Block */}
        <div
          className={`flex items-center gap-2 pl-2 border-l ${
            isResearch ? 'border-slate-200' : 'border-[#262b35]'
          }`}
        >
          <div className="hidden text-right lg:block">
            <p
              className={`text-[11px] font-semibold font-mono ${
                isResearch ? 'text-slate-700' : 'text-slate-300'
              }`}
            >
              {user?.username ?? t.header.operatorRole}
            </p>
            <p
              className={`text-[9px] font-mono tracking-widest font-bold ${
                isResearch ? 'text-blue-700' : 'text-[#06b6d4]'
              }`}
            >
              {user?.role?.toUpperCase() ?? t.header.levelAuth}
            </p>
          </div>
          <div
            className={`w-8 h-8 border overflow-hidden select-none flex items-center justify-center text-xs font-bold text-white ${
              isResearch ? 'rounded-lg border-slate-200' : 'rounded-sm border-[#262b35]'
            }`}
            style={{ backgroundColor: avatarColor }}
          >
            {user ? user.username.charAt(0).toUpperCase() : 'S'}
          </div>
        </div>
      </div>
    </header>
  );
}
