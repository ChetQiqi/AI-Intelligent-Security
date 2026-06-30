import type { FaceEvent } from '../types/api';

interface RecentRecognitionPollerOptions {
  fetchEvents: (signal: AbortSignal) => Promise<FaceEvent[]>;
  onData: (events: FaceEvent[]) => void;
  onError: (error: Error) => void;
  intervalMs?: number;
  scheduleInterval?: (callback: () => void, delay: number) => number;
  cancelInterval?: (id: number) => void;
  subscribeVisibility?: (callback: () => void) => () => void;
  isVisible?: () => boolean;
}

export function createRecentRecognitionPoller({
  fetchEvents,
  onData,
  onError,
  intervalMs = 5_000,
  scheduleInterval = (callback, delay) => window.setInterval(callback, delay),
  cancelInterval = (id) => window.clearInterval(id),
  subscribeVisibility = (callback) => {
    document.addEventListener('visibilitychange', callback);
    return () => document.removeEventListener('visibilitychange', callback);
  },
  isVisible = () => document.visibilityState === 'visible',
}: RecentRecognitionPollerOptions): () => void {
  let stopped = false;
  let requestInFlight = false;
  let activeController: AbortController | null = null;

  const refresh = async () => {
    if (stopped || requestInFlight) {
      return;
    }

    requestInFlight = true;
    const controller = new AbortController();
    activeController = controller;

    try {
      const events = await fetchEvents(controller.signal);
      if (!stopped) {
        onData(events);
      }
    } catch (error) {
      if (!stopped && !(error instanceof DOMException && error.name === 'AbortError')) {
        onError(error instanceof Error ? error : new Error('近期识别记录更新失败'));
      }
    } finally {
      if (activeController === controller) {
        activeController = null;
      }
      requestInFlight = false;
    }
  };

  const intervalId = scheduleInterval(() => {
    void refresh();
  }, intervalMs);
  const unsubscribeVisibility = subscribeVisibility(() => {
    if (isVisible()) {
      void refresh();
    }
  });

  void refresh();

  return () => {
    stopped = true;
    cancelInterval(intervalId);
    unsubscribeVisibility();
    activeController?.abort();
    activeController = null;
  };
}
