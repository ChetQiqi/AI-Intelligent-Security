/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useCallback, useRef, useState } from 'react';
import { AlertOctagon } from 'lucide-react';
import AdminPanel from './components/AdminPanel';
import AIPortraitView from './components/AIPortraitView';
import ApiSimulator from './components/ApiSimulator';
import DashboardView from './components/DashboardView';
import DeveloperConsoleView from './components/DeveloperConsoleView';
import Header from './components/Header';
import ImageRecognitionView from './components/ImageRecognitionView';
import LoginPage from './components/LoginPage';
import PeopleManagementView from './components/PeopleManagementView';
import SecurityAnalyticsView from './components/SecurityAnalyticsView';
import Sidebar from './components/Sidebar';
import ToastContainer from './components/ToastContainer';
import VideoAnalysisView from './components/VideoAnalysisView';
import { useAuth } from './hooks/useAuth';
import { LOCALES, type Language } from './locales';
import type { LogLine } from './types';

export default function App() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [language, setLanguage] = useState<Language>('zh');
  const [isLockedDown, setIsLockedDown] = useState(false);
  const [logsList, setLogsList] = useState<LogLine[]>([]);
  const [isApiSimulatorOpen, setIsApiSimulatorOpen] = useState(false);
  const addLogRef = useRef<
    ((level: LogLine['level'], message: string) => void) | undefined
  >(undefined);

  const addLog = useCallback((level: LogLine['level'], message: string) => {
    const now = new Date();
    const timestamp =
      now.toLocaleTimeString('en-GB') +
      '.' +
      String(now.getMilliseconds()).padStart(3, '0').slice(0, 2);
    setLogsList((previous) => [...previous, { timestamp, level, message }]);
  }, []);

  addLogRef.current = addLog;

  const handleEmergencyLockdown = () => {
    if (isLockedDown) {
      setIsLockedDown(false);
      addLog('INFO', 'SYSTEM_LOCKDOWN: Re-entry authorization confirmed.');
      addLog('RESULT', 'RE_ENTRY: All systems restored to standard operational frames.');
      return;
    }
    setIsLockedDown(true);
    addLog('ERROR', 'SYSTEM_LOCKDOWN: CRISIS ALERT triggered!');
    addLog('WARNING', 'LOCKDOWN: Isolating peripheral entry paths...');
  };

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#090b11]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-500 font-mono uppercase tracking-widest">
            Initializing Sentinel Core...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderActiveView = () => {
    if (isLockedDown) return null;
    const isDeveloper = user?.role === 'developer' || user?.role === 'admin';

    return (
      <>
        <div className={activeTab === 'dashboard' ? '' : 'hidden'}>
          <DashboardView setActiveTab={setActiveTab} language={language} />
        </div>
        <div className={activeTab === 'people' ? '' : 'hidden'}>
          <PeopleManagementView addLog={addLog} language={language} />
        </div>
        <div className={activeTab === 'portrait' ? '' : 'hidden'}>
          <AIPortraitView addLog={addLog} language={language} />
        </div>
        <div className={activeTab === 'recognition' ? '' : 'hidden'}>
          <ImageRecognitionView logs={logsList} addLog={addLog} language={language} />
        </div>
        <div className={activeTab === 'video' ? '' : 'hidden'}>
          <VideoAnalysisView addLog={addLog} language={language} />
        </div>
        <div className={activeTab === 'security' ? 'h-full overflow-auto' : 'hidden'}>
          <SecurityAnalyticsView language={language} />
        </div>
        {isDeveloper && (
          <div className={activeTab === 'developer' ? '' : 'hidden'}>
            <DeveloperConsoleView addLog={addLog} language={language} />
          </div>
        )}
        {user?.role === 'admin' && (
          <div className={activeTab === 'admin' ? '' : 'hidden'}>
            <AdminPanel addLog={addLog} language={language} />
          </div>
        )}
      </>
    );
  };

  const getHeaderTitle = () => {
    const t = LOCALES[language];
    switch (activeTab) {
      case 'dashboard':
        return `System_v4.2.1 — ${t.sidebar.dashboard}`;
      case 'people':
        return t.people.title;
      case 'portrait':
        return t.portrait.title;
      case 'recognition':
        return t.recognition.title;
      case 'video':
        return t.video.cctvTitle;
      case 'security':
        return language === 'zh' ? '安防驾驶舱' : 'Security Cockpit';
      case 'developer':
        return t.developer.title;
      case 'admin':
        return 'Admin Panel';
      default:
        return t.sidebar.appName;
    }
  };

  const t = LOCALES[language];
  const shellAppearance = 'dark';

  return (
    <div
      className="flex h-screen w-screen overflow-hidden bg-[#090b11] font-sans text-slate-300 antialiased"
    >
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onEmergencyLockdown={handleEmergencyLockdown}
        isLockedDown={isLockedDown}
        language={language}
        user={user}
        appearance={shellAppearance}
      />

      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        <Header
          title={getHeaderTitle()}
          searchPlaceholder={
            activeTab === 'people' ? t.people.searchPlaceholder : t.header.placeholder
          }
          toggleApiSimulator={() => setIsApiSimulatorOpen((previous) => !previous)}
          language={language}
          onChangeLanguage={setLanguage}
          user={user}
          appearance={shellAppearance}
        />

        <main className="flex-1 min-h-0 relative">
          {renderActiveView()}
          {isLockedDown && (
            <div className="absolute inset-0 z-40 bg-black/95 flex flex-col items-center justify-center p-8 select-none font-mono">
              <div className="absolute inset-0 bg-red-950/10 animate-pulse pointer-events-none border-2 border-red-500/30" />
              <div className="w-full max-w-xl text-center space-y-8 relative z-10 p-10 bg-[#0d0708] border border-red-900 shadow-2xl shadow-red-500/10 rounded-sm">
                <AlertOctagon className="w-16 h-16 text-red-500 mx-auto animate-pulse" />
                <h2 className="text-xl font-black tracking-[0.2em] text-red-500 uppercase">
                  {t.lockdown.crisisAlert}
                </h2>
                <p className="text-xs text-red-300 max-w-md mx-auto leading-relaxed">
                  {t.lockdown.crisisDesc}
                </p>
                <button
                  onClick={handleEmergencyLockdown}
                  className="w-full py-4 bg-emerald-500 hover:bg-emerald-600 font-extrabold uppercase rounded-sm text-slate-950 text-xs tracking-widest transition-all cursor-pointer"
                >
                  {t.lockdown.deactivateBtn}
                </button>
              </div>
            </div>
          )}
        </main>
      </div>

      <ApiSimulator
        isOpen={isApiSimulatorOpen}
        onClose={() => setIsApiSimulatorOpen(false)}
        language={language}
      />
      <ToastContainer />
    </div>
  );
}
