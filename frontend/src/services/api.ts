import type {
  CampaignRequest,
  CampaignResponse,
  CampaignResults,
} from "@/types/campaign";

const API_BASE_URL = "http://localhost:8000/api";

// Helper function for API calls with timeout and better error handling
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // Handle specific HTTP status codes
      if (response.status === 404) {
        throw new Error(`Endpoint not found: ${endpoint}`);
      } else if (response.status === 500) {
        throw new Error(`Server error: ${response.statusText}`);
      } else if (response.status === 422) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Validation error: ${JSON.stringify(errorData)}`);
      } else {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
    }

    const data = await response.json();
    
    // Basic validation of the response data
    if (data === null || data === undefined) {
      throw new Error("API returned empty response");
    }
    
    return data as T;
  } catch (error) {
    clearTimeout(timeoutId);
    
    // Handle fetch errors
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout: ${endpoint} took longer than 30 seconds`);
      } else if (error.message.includes('fetch')) {
        throw new Error(`Network error: Unable to reach server at ${API_BASE_URL}`);
      }
    }
    
    console.error(`API error for ${endpoint}:`, error);
    throw error;
  }
}

// Campaign API methods
export const campaignApi = {
  // Create a new campaign
  create: (data: CampaignRequest) =>
    apiCall<CampaignResponse>("/campaigns/create", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Get campaign status
  getStatus: (id: string) =>
    apiCall<CampaignResponse>(`/campaigns/${id}/status`),

  // Get campaign results
  getResults: (id: string) =>
    apiCall<CampaignResults>(`/campaigns/${id}/results`),

};

// Health check API
export const healthApi = {
  check: () => apiCall<{ status: string }>("/health"),

  getAgentStatus: () =>
    apiCall<{ agents: Array<{ name: string; status: string }> }>(
      "/agents/status"
    ),
};