import type {
  CampaignRequest,
  CampaignResponse,
  CampaignResults,
} from "@/types/campaign";

const API_BASE_URL = "http://localhost:8080/api";

// Helper function for API calls
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Basic validation of the response data
    if (data === null || data === undefined) {
      throw new Error("API returned empty response");
    }
    
    return data as T;
  } catch (error) {
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

  // Force complete a campaign (for demo purposes)
  forceComplete: (id: string) =>
    apiCall<CampaignResponse>(`/campaigns/${id}/force-complete`, {
      method: "POST",
    }),
};

// Health check API
export const healthApi = {
  check: () => apiCall<{ status: string }>("/health"),

  getAgentStatus: () =>
    apiCall<{ agents: Array<{ name: string; status: string }> }>(
      "/agents/status"
    ),
};
