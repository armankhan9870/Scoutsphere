/** API Client helper attaching JWT token to outgoing backend requests and URL helpers. */

const API_BASE_URL = '/api/v1';

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  isRetry: boolean = false
): Promise<T> {
  const token = localStorage.getItem('scoutsphere_access_token');

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Set default JSON Content-Type if not FormData
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
    credentials: 'include',
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);

  if (response.status === 401 && !isRetry && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/signup') && !endpoint.includes('/auth/refresh')) {
    // Attempt silent refresh via httpOnly refresh cookie
    try {
      const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        if (refreshData.access_token) {
          localStorage.setItem('scoutsphere_access_token', refreshData.access_token);
          headers['Authorization'] = `Bearer ${refreshData.access_token}`;
          const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
            credentials: 'include',
          });
          if (retryResponse.ok) {
            return retryResponse.json();
          }
        }
      }
    } catch {
      // Refresh failed
      localStorage.removeItem('scoutsphere_access_token');
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

/** Utility to guarantee external URLs begin with http:// or https:// to prevent 404 relative routing. */
export const getValidExternalUrl = (url?: string, title?: string, company?: string): string => {
  if (!url || url.trim() === '' || url === '#' || url === 'undefined') {
    const query = encodeURIComponent(`${title || ''} ${company || ''} careers apply`.trim() || 'jobs');
    return `https://www.google.com/search?q=${query}`;
  }
  let trimmed = url.trim();
  if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
    return `https://${trimmed}`;
  }
  return trimmed;
};

/** Downloads the tailored resume file as a clean Blob trigger without tab authentication errors. */
export const downloadTailoredResumeFile = async (oppId?: string) => {
  try {
    const targetOppId = oppId || '93080d6b-a6ee-4710-9ddc-b77896618db4';
    const response = await fetch(`${API_BASE_URL}/applications/download-resume/f8a92b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c?opportunity_id=${targetOppId}`);
    if (!response.ok) {
      window.open(`http://127.0.0.1:8000/api/v1/applications/download-resume/f8a92b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c?opportunity_id=${targetOppId}`, '_blank');
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Tailored_Resume_Alex_Rivera.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch {
    window.open(`http://127.0.0.1:8000/api/v1/applications/download-resume/f8a92b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c?opportunity_id=${oppId}`, '_blank');
  }
};

/** Downloads complete JSON dump of user profile, resumes, matches, applications, and settings. */
export const downloadUserDataExport = async () => {
  const data = await apiFetch<any>('/settings/privacy/export');
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ScoutSphere_Data_Export_${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

/** Triggers standalone general ATS Analysis for a given resume ID. */
export const analyzeAtsResume = async (resumeId: string) => {
  return apiFetch<any>(`/resumes/${resumeId}/ats-analysis`, {
    method: 'POST',
  });
};

