/**
 * API Client with Session Expiry Detection
 *
 * Provides Fetch API wrapper with automatic session expiry detection (T039).
 *
 * Features:
 * - Detects 401 responses indicating session expiry
 * - Redirects to /login?session_expired=true for user notification (FR-014)
 * - Includes credentials (cookies) with all requests
 * - Type-safe API for making authenticated requests
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

/**
 * Get API base URL - uses default since Docusaurus doesn't expose customFields to non-component modules.
 * The actual API URL should be set in .env or docusaurus.config.ts customFields.
 */
function getApiBaseUrl(): string {
  // Check if running in browser and if there's a global config
  if (typeof window !== 'undefined' && (window as any).docusaurusConfig?.customFields?.API_URL) {
    return (window as any).docusaurusConfig.customFields.API_URL as string;
  }
  // Default to localhost for development
  return  'http://localhost:8001'; // Force it to 8001
}

/**
 * Custom fetch wrapper with session expiry detection
 *
 * @param url API endpoint path (relative to API_BASE_URL)
 * @param options Fetch options
 * @returns Promise with Response
 * @throws Redirects to login on 401 (session expired)
 */
export async function apiClient(url: string, options: RequestInit = {}): Promise<Response> {
  const API_BASE_URL = getApiBaseUrl();
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;

  const defaultOptions: RequestInit = {
    credentials: 'include', // Always send cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(fullUrl, defaultOptions);

    // Session expiry detection (T039)
    if (response.status === 401) {
      // Special handling: if already on login page, don't redirect again
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        // Redirect to login with session expired message
        window.location.href = '/login?session_expired=true';
      }
    }

    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Helper function for GET requests
 */
export async function apiGet(url: string): Promise<Response> {
  return apiClient(url, { method: 'GET' });
}

/**
 * Helper function for POST requests
 */
export async function apiPost(url: string, data?: any): Promise<Response> {
  return apiClient(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper function for PUT requests
 */
export async function apiPut(url: string, data?: any): Promise<Response> {
  return apiClient(url, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper function for DELETE requests
 */
export async function apiDelete(url: string): Promise<Response> {
  return apiClient(url, { method: 'DELETE' });
}
