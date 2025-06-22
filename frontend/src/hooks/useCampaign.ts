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
  });
};

// Hook to get campaign status with polling
export const useCampaignStatus = (id: string | undefined, enabled = true) => {
  return useQuery({
    queryKey: ["campaign", "status", id],
    queryFn: () => campaignApi.getStatus(id!),
    enabled: !!id && enabled,
    refetchInterval: (query) => {
      // Poll every 3 seconds if campaign is processing
      const data = query.state.data;
      if (data?.status === "processing") {
        return 3000;
      }
      return false;
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
  });
};

// Hook to force complete a campaign
export const useForceCompleteCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignApi.forceComplete(id),
    onSuccess: (_, variables) => {
      // Invalidate status and results queries for this campaign
      queryClient.invalidateQueries({
        queryKey: ["campaign", "status", variables],
      });
      queryClient.invalidateQueries({
        queryKey: ["campaign", "results", variables],
      });
    },
  });
};
