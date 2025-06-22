// Campaign request types
export interface CampaignRequest {
  business_name: string;
  industry: string;
  campaign_goal: string;
  target_platforms: string[];
  brand_voice: string;
  target_audience?: string;
  keywords?: string[];
  budget_range?: string;
}

// Campaign response types
export interface CampaignResponse {
  campaign_id: string;
  status: "processing" | "completed" | "failed";
  agent_progress: AgentProgress[];
  created_at: string;
  completed_at?: string;
}

// Agent progress tracking
export interface AgentProgress {
  agent_name:
    | "trend_analyzer"
    | "content_writer"
    | "visual_designer"
    | "campaign_scheduler";
  status: "pending" | "running" | "completed" | "error";
  progress_percentage: number;
  message: string;
  ai_generated?: boolean;
}

// Complete campaign results
export interface CampaignResults {
  trends: TrendAnalysis;
  content: PlatformContent;
  visuals: VisualAssets;
  schedule: SchedulingData;
  performance_predictions: PerformancePredictions;
}

// Trend analysis types
export interface TrendAnalysis {
  trending_topics: TrendingTopic[];
  viral_probability: string;
  peak_engagement_window: string;
  trending_hashtags: string[];
}

export interface TrendingTopic {
  topic: string;
  relevance_score: number;
  trend_type: "rising" | "trending" | "stable";
}

// Content types
export interface PlatformContent {
  instagram?: SocialMediaPost;
  tiktok?: SocialMediaPost;
  facebook?: SocialMediaPost;
  linkedin?: SocialMediaPost;
  twitter?: SocialMediaPost;
}

export interface SocialMediaPost {
  text: string;
  hashtags: string[];
  character_count: number;
  viral_elements: string[];
  engagement_tactics?: string[];
}

// Visual assets types
export interface VisualAssets {
  image_suggestions: UnsplashImage[];
  recommended_style: string;
  color_palette: string[];
}

export interface UnsplashImage {
  id: string;
  url: string;
  photographer: string;
  photographer_url: string;
  description: string;
  alt_description: string;
  likes: number;
  width: number;
  height: number;
}

// Scheduling types
export interface SchedulingData {
  optimal_times: OptimalTime[];
  best_days: string[];
  posting_frequency: string;
  timezone: string;
}

export interface OptimalTime {
  platform: string;
  day: string;
  time: string;
  engagement_score: number;
}

// Performance prediction types
export interface PerformancePredictions {
  viral_probability: string;
  estimated_reach: string;
  engagement_rate: string;
  roi_prediction: string;
  confidence_score: number;
  metrics_breakdown: MetricsBreakdown;
}

export interface MetricsBreakdown {
  likes_estimate: string;
  shares_estimate: string;
  comments_estimate: string;
  impressions_estimate: string;
}
