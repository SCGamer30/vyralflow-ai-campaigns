import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sparkles as SparklesComponent } from "@/components/ui/sparkles";
import { useCampaignResults } from "@/hooks/useCampaign";
import {
  ArrowLeft,
  Download,
  Share2,
  TrendingUp,
  Hash,
  Clock,
  Target,
  Users,
  DollarSign,
  BarChart3,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  Music2,
  Image as ImageIcon,
  Calendar,
  Heart,
  Copy,
  Check,
  Zap,
  Star,
} from "lucide-react";

const platformIcons = {
  instagram: Instagram,
  tiktok: Music2,
  facebook: Facebook,
  linkedin: Linkedin,
  twitter: Twitter,
};

export function CampaignResults() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: results, isLoading, error } = useCampaignResults(id);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const handleCopyContent = (text: string, platform: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(platform);
    setTimeout(() => setCopiedText(null), 2000);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="h-12 w-12 animate-pulse text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading campaign results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <p className="text-gray-600 text-center mb-4">
              Failed to load campaign results. Please try again.
            </p>
            <Button onClick={() => navigate("/create")} className="w-full">
              Create New Campaign
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getViralProbabilityColor = (probability: string) => {
    const value = parseInt(probability.match(/\d+/)?.[0] || "0");
    if (value >= 80) return "text-green-600";
    if (value >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Enhanced Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
      <SparklesComponent 
        className="opacity-40" 
        particleColor="#f472b6" 
        particleDensity={60}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-pink-900/10 via-transparent to-amber-900/10" />

      {/* Header */}
      <div className="relative z-50 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <Button
                variant="ghost"
                onClick={() => navigate("/create")}
                className="text-gray-300 hover:text-white hover:bg-white/10"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Create New Campaign
              </Button>
              <div className="w-px h-6 bg-gray-600" />
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-pink-500 to-amber-500 rounded-lg flex items-center justify-center">
                  <Star className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">Campaign Results</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <Button 
                variant="outline" 
                size="sm"
                className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 relative z-10 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-black/40 backdrop-blur-lg border border-green-500/30 mb-6"
            >
              <Check className="w-5 h-5 text-green-400" />
              <span className="text-sm font-medium text-white">
                Campaign Complete
              </span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </motion.div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              <span className="bg-gradient-to-r from-pink-400 via-rose-400 to-amber-400 bg-clip-text text-transparent">
                Viral Campaign
              </span>
              <span className="block text-3xl md:text-4xl mt-2">
                Ready to Launch!
              </span>
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Your AI-generated viral campaign is optimized for maximum engagement and ready to dominate social media
            </p>
          </motion.div>

          {/* Key Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-8"
          >
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black/20 backdrop-blur-lg border border-pink-500/30 mb-4"
              >
                <Zap className="w-5 h-5 text-pink-400" />
                <span className="text-sm font-medium text-white">
                  Performance Predictions
                </span>
              </motion.div>
              <h2 className="text-3xl font-bold text-white mb-2">AI-Powered Analytics</h2>
              <p className="text-gray-300">Advanced metrics based on real-time trend analysis</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden group hover:border-pink-400/40 transition-all duration-300">
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <SparklesComponent 
                      particleColor="#f472b6" 
                      particleDensity={20}
                      minSize={1}
                      maxSize={3}
                    />
                  </div>
                  <CardContent className="pt-6 relative z-10">
                    <div className="flex items-center justify-between mb-3">
                      <Target className="h-8 w-8 text-pink-400" />
                      <Badge className="bg-pink-400/20 text-pink-300 border-pink-400/30">AI Prediction</Badge>
                    </div>
                    <p className={`text-3xl font-bold mb-2 ${
                      getViralProbabilityColor(results.performance_predictions.viral_probability)
                    }`}>
                      {results.performance_predictions.viral_probability}
                    </p>
                    <p className="text-sm text-gray-400">Viral Probability</p>
                  </CardContent>
                </Card>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden group hover:border-blue-400/40 transition-all duration-300">
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <SparklesComponent 
                      particleColor="#3b82f6" 
                      particleDensity={20}
                      minSize={1}
                      maxSize={3}
                    />
                  </div>
                  <CardContent className="pt-6 relative z-10">
                    <div className="flex items-center justify-between mb-3">
                      <Users className="h-8 w-8 text-blue-400" />
                    </div>
                    <p className="text-3xl font-bold text-white mb-2">
                      {results.performance_predictions.estimated_reach}
                    </p>
                    <p className="text-sm text-gray-400">Estimated Reach</p>
                  </CardContent>
                </Card>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden group hover:border-green-400/40 transition-all duration-300">
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <SparklesComponent 
                      particleColor="#22c55e" 
                      particleDensity={20}
                      minSize={1}
                      maxSize={3}
                    />
                  </div>
                  <CardContent className="pt-6 relative z-10">
                    <div className="flex items-center justify-between mb-3">
                      <BarChart3 className="h-8 w-8 text-green-400" />
                    </div>
                    <p className="text-3xl font-bold text-white mb-2">
                      {results.performance_predictions.engagement_rate}
                    </p>
                    <p className="text-sm text-gray-400">Engagement Rate</p>
                  </CardContent>
                </Card>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.7 }}
              >
                <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden group hover:border-yellow-400/40 transition-all duration-300">
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <SparklesComponent 
                      particleColor="#fbbf24" 
                      particleDensity={20}
                      minSize={1}
                      maxSize={3}
                    />
                  </div>
                  <CardContent className="pt-6 relative z-10">
                    <div className="flex items-center justify-between mb-3">
                      <DollarSign className="h-8 w-8 text-yellow-400" />
                    </div>
                    <p className="text-3xl font-bold text-white mb-2">
                      {results.performance_predictions.roi_prediction}
                    </p>
                    <p className="text-sm text-gray-400">ROI Prediction</p>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </motion.div>

          {/* Main Content Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <Tabs defaultValue="trends" className="space-y-6">
              <TabsList className="grid w-full grid-cols-4 bg-black/20 backdrop-blur-lg border border-gray-600/30">
                <TabsTrigger value="trends" className="data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-300">Trends</TabsTrigger>
                <TabsTrigger value="content" className="data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-300">Content</TabsTrigger>
                <TabsTrigger value="visuals" className="data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-300">Visuals</TabsTrigger>
                <TabsTrigger value="schedule" className="data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-300">Schedule</TabsTrigger>
              </TabsList>

            {/* Trends Tab */}
            <TabsContent value="trends" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden">
                  <div className="absolute inset-0 opacity-20">
                    <SparklesComponent 
                      particleColor="#f472b6" 
                      particleDensity={15}
                      minSize={1}
                      maxSize={3}
                    />
                  </div>
                  <CardHeader className="relative z-10">
                    <CardTitle className="flex items-center gap-2 text-white">
                      <TrendingUp className="h-6 w-6 text-pink-400" />
                      Trend Analysis
                    </CardTitle>
                    <CardDescription className="text-gray-300">
                      AI-discovered trends and viral opportunities
                    </CardDescription>
                  </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold mb-3">Trending Topics</h3>
                      <div className="space-y-3">
                        {results.trends.trending_topics.map((topic, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <div>
                              <p className="font-medium">{topic.topic}</p>
                              <p className="text-sm text-gray-600">
                                {topic.trend_type}
                              </p>
                            </div>
                            <Badge
                              variant={
                                topic.relevance_score > 85
                                  ? "completed"
                                  : "secondary"
                              }
                            >
                              {topic.relevance_score}% match
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-3">Viral Elements</h3>
                      <div className="bg-purple-50 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Clock className="h-4 w-4 text-purple-600" />
                          <p className="font-medium">Peak Engagement Window</p>
                        </div>
                        <p className="text-purple-900">
                          {results.trends.peak_engagement_window}
                        </p>
                      </div>
                      <div className="mt-4">
                        <p className="font-medium mb-2">Trending Hashtags</p>
                        <div className="flex flex-wrap gap-2">
                          {results.trends.trending_hashtags?.map(
                            (hashtag, index) => (
                              <Badge key={index} variant="outline">
                                <Hash className="h-3 w-3 mr-1" />
                                {hashtag.replace("#", "")}
                              </Badge>
                            )
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              </motion.div>
            </TabsContent>

            {/* Content Tab */}
            <TabsContent value="content" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Platform-Specific Content</CardTitle>
                  <CardDescription>
                    AI-generated content optimized for each platform
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs
                    defaultValue={Object.keys(results.content)[0]}
                    className="w-full"
                  >
                    <TabsList className="grid grid-cols-5 w-full mb-4">
                      {Object.entries(results.content).map(([platform]) => {
                        const Icon =
                          platformIcons[platform as keyof typeof platformIcons];
                        return (
                          <TabsTrigger
                            key={platform}
                            value={platform}
                            className="gap-2"
                          >
                            <Icon className="h-4 w-4" />
                            <span className="hidden sm:inline">
                              {platform.charAt(0).toUpperCase() +
                                platform.slice(1)}
                            </span>
                          </TabsTrigger>
                        );
                      })}
                    </TabsList>
                    {Object.entries(results.content).map(
                      ([platform, content]) => (
                        <TabsContent key={platform} value={platform}>
                          <div className="space-y-4">
                            <div className="bg-gray-50 rounded-lg p-4">
                              <div className="flex justify-between items-start mb-3">
                                <h4 className="font-medium">Post Content</h4>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() =>
                                    handleCopyContent(content.text, platform)
                                  }
                                >
                                  {copiedText === platform ? (
                                    <>
                                      <Check className="h-4 w-4 mr-1" />
                                      Copied
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="h-4 w-4 mr-1" />
                                      Copy
                                    </>
                                  )}
                                </Button>
                              </div>
                              <p className="text-gray-700 whitespace-pre-wrap">
                                {content.text}
                              </p>
                              <p className="text-sm text-gray-500 mt-2">
                                {content.character_count} characters
                              </p>
                            </div>
                            <div>
                              <h4 className="font-medium mb-2">Hashtags</h4>
                              <div className="flex flex-wrap gap-2">
                                {content.hashtags.map((tag: string, index: number) => (
                                  <Badge key={index} variant="secondary">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            {content.viral_elements && (
                              <div>
                                <h4 className="font-medium mb-2">
                                  Viral Elements
                                </h4>
                                <div className="grid grid-cols-2 gap-2">
                                  {content.viral_elements.map(
                                    (element: string, index: number) => (
                                      <div
                                        key={index}
                                        className="flex items-center gap-2 text-sm text-gray-600"
                                      >
                                        <Check className="h-3 w-3 text-green-600" />
                                        {element}
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        </TabsContent>
                      )
                    )}
                  </Tabs>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Visuals Tab */}
            <TabsContent value="visuals" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ImageIcon className="h-5 w-5" />
                    Visual Assets
                  </CardTitle>
                  <CardDescription>
                    Professional images curated by AI from Unsplash
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Recommended Style</h3>
                      <p className="text-gray-600">
                        {results.visuals.recommended_style}
                      </p>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Color Palette</h3>
                      <div className="flex gap-2">
                        {results.visuals.color_palette.map((color, index) => (
                          <div
                            key={index}
                            className="w-16 h-16 rounded-lg shadow-sm flex items-center justify-center text-xs font-mono"
                            style={{ backgroundColor: color }}
                          >
                            <span className="bg-white/80 px-1 rounded">
                              {color}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-4">
                        Curated Images (
                        {results.visuals.image_suggestions.length})
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {results.visuals.image_suggestions.map(
                          (image, index) => (
                            <motion.div
                              key={image.id}
                              initial={{ opacity: 0, scale: 0.9 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{
                                duration: 0.3,
                                delay: index * 0.05,
                              }}
                              className="group relative rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-shadow"
                            >
                              <img
                                src={image.url}
                                alt={image.alt_description || image.description}
                                className="w-full h-48 object-cover"
                              />
                              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                                <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
                                  <p className="text-sm font-medium truncate">
                                    {image.description}
                                  </p>
                                  <div className="flex items-center justify-between mt-1">
                                    <a
                                      href={image.photographer_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs hover:underline"
                                    >
                                      by {image.photographer}
                                    </a>
                                    <div className="flex items-center gap-1 text-xs">
                                      <Heart className="h-3 w-3" />
                                      {image.likes}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          )
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Schedule Tab */}
            <TabsContent value="schedule" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Optimal Posting Schedule
                  </CardTitle>
                  <CardDescription>
                    AI-optimized timing for maximum engagement
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold mb-3">Best Days to Post</h3>
                      <div className="space-y-2">
                        {results.schedule.best_days.map((day, index) => (
                          <div
                            key={index}
                            className="flex items-center gap-2 p-2 bg-green-50 rounded"
                          >
                            <Calendar className="h-4 w-4 text-green-600" />
                            <span className="font-medium">{day}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-3">
                        Platform-Specific Times
                      </h3>
                      <div className="space-y-3">
                        {results.schedule.optimal_times.map((time, index) => {
                          const Icon =
                            platformIcons[
                              time.platform as keyof typeof platformIcons
                            ];
                          return (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                            >
                              <div className="flex items-center gap-3">
                                <Icon className="h-5 w-5" />
                                <div>
                                  <p className="font-medium">{time.platform}</p>
                                  <p className="text-sm text-gray-600">
                                    {time.day} at {time.time}
                                  </p>
                                </div>
                              </div>
                              <Badge variant="secondary">
                                {time.engagement_score}% engagement
                              </Badge>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <p className="font-medium">Posting Frequency</p>
                    </div>
                    <p className="text-blue-900">
                      {results.schedule.posting_frequency}
                    </p>
                    <p className="text-sm text-blue-700 mt-1">
                      Timezone: {results.schedule.timezone}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
          </motion.div>

          {/* Performance Predictions Details */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Detailed Performance Predictions</CardTitle>
              <CardDescription>
                AI-powered metrics breakdown for your campaign
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(
                  results.performance_predictions.metrics_breakdown
                ).map(([metric, value]) => (
                  <div
                    key={metric}
                    className="text-center p-4 bg-gray-50 rounded-lg"
                  >
                    <p className="text-2xl font-bold text-purple-600">
                      {value}
                    </p>
                    <p className="text-sm text-gray-600 capitalize">
                      {metric.replace("_estimate", "").replace("_", " ")}
                    </p>
                  </div>
                ))}
              </div>
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-green-900">
                      Confidence Score
                    </p>
                    <p className="text-sm text-green-700">
                      Based on AI analysis and market trends
                    </p>
                  </div>
                  <Badge variant="completed" className="text-lg px-4 py-2">
                    {results.performance_predictions.confidence_score}%
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <Card className="mt-8 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
            <CardContent className="pt-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">
                  Ready to Launch Your Campaign?
                </h2>
                <p className="mb-6 text-white/90">
                  Your AI-generated viral campaign is ready to go live
                </p>
                <div className="flex gap-4 justify-center">
                  <Button
                    variant="secondary"
                    size="lg"
                    onClick={() => navigate("/create")}
                  >
                    Create Another Campaign
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                  >
                    <Share2 className="w-4 h-4 mr-2" />
                    Share Results
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
