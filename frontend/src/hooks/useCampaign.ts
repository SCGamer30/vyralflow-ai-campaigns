import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignApi } from "@/services/api";
import type { CampaignRequest } from "@/types/campaign";

// Hook to create a new campaign
export const useCreateCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CampaignRequest) => campaignApi.create(data),
    onSuccess: (data) => {
      // Invalidate any relevant queries
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      return data;
    },
    retry: 1, // Retry once for network errors
    onError: (error) => {
      console.error("Campaign creation failed:", error);
    },
  });
};

// Hook to get campaign status with polling and error handling
export const useCampaignStatus = (id: string | undefined, enabled = true) => {
  return useQuery({
    queryKey: ["campaign", "status", id],
    queryFn: () => campaignApi.getStatus(id!),
    enabled: !!id && enabled,
    refetchInterval: (query) => {
      // Stop polling if there's an error
      if (query.state.error) {
        return false;
      }
      
      // Poll every 3 seconds if campaign is processing
      const data = query.state.data;
      if (data?.status === "processing") {
        return 3000;
      }
      return false;
    },
    retry: (failureCount, error) => {
      // Retry up to 3 times for network errors, but not for 404s
      if (error instanceof Error && error.message.includes('404')) {
        return false;
      }
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 1000, // Data is fresh for 1 second
    onError: (error) => {
      console.error("Campaign status polling failed:", error);
    },
  });
};

// Hook to get campaign results
export const useCampaignResults = (id: string | undefined) => {
  return useQuery({
    queryKey: ["campaign", "results", id],
    queryFn: () => campaignApi.getResults(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
    retry: 2,
    onError: (error) => {
      console.error("Failed to fetch campaign results:", error);
    },
  });
};