/// <reference types="vite/client" />

const API_BASE: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // Response is not JSON.
    }
    throw new ApiError(response.status, detail);
  }
  const body = await response.text();
  return body ? (JSON.parse(body) as T) : ({} as T);
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  return handleResponse<T>(
    await fetch(`${API_BASE}${path}`, {
      headers: getAuthHeaders(),
      signal,
    }),
  );
}

export async function apiPost<T>(
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  const isFormData = body instanceof FormData;
  return handleResponse<T>(
    await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      },
      body: isFormData ? body : JSON.stringify(body),
      signal,
    }),
  );
}

export async function apiPut<T>(
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  return handleResponse<T>(
    await fetch(`${API_BASE}${path}`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal,
    }),
  );
}

export async function apiDelete<T>(path: string, signal?: AbortSignal): Promise<T> {
  return handleResponse<T>(
    await fetch(`${API_BASE}${path}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
      signal,
    }),
  );
}

export async function apiUpload<T>(
  path: string,
  formData: FormData,
  signal?: AbortSignal,
): Promise<T> {
  return apiPost<T>(path, formData, signal);
}

export function apiUploadWithProgress<T>(
  path: string,
  formData: FormData,
  onProgress: (pct: number) => void,
  signal?: AbortSignal,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE}${path}`);
    Object.entries(getAuthHeaders()).forEach(([key, value]) => {
      xhr.setRequestHeader(key, value);
    });
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    });
    signal?.addEventListener('abort', () => xhr.abort());
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.responseText ? JSON.parse(xhr.responseText) : ({} as T));
        return;
      }
      let detail = xhr.statusText;
      try {
        detail = JSON.parse(xhr.responseText).detail ?? detail;
      } catch {
        // Response is not JSON.
      }
      reject(new ApiError(xhr.status, detail));
    });
    xhr.addEventListener('error', () => reject(new ApiError(0, 'Network error')));
    xhr.addEventListener('abort', () => reject(new ApiError(0, 'Upload cancelled')));
    xhr.send(formData);
  });
}
