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
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  Image as ImageIcon,
  Heart,
  Copy,
  Check,
  BarChart3,
} from "lucide-react";

const platformIcons = {
  instagram: Instagram,
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

  
  // Helper function to safely access nested properties
  const safelyGet = (obj: any, path: string, defaultValue: any = null) => {
    try {
      const keys = path.split('.');
      return keys.reduce((o, key) => (o && o[key] !== undefined) ? o[key] : defaultValue, obj);
    } catch (e) {
      console.error(`Error accessing path ${path}:`, e);
      return defaultValue;
    }
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
                <img 
                  src="/vyralflow.png" 
                  alt="VyralFlow AI Logo" 
                  className="w-8 h-8 object-contain"
                />
                <span className="text-xl font-bold text-white">Campaign Results</span>
              </div>
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


          {/* Main Content Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <Tabs defaultValue="content" className="space-y-6">
              <TabsList className="grid w-full grid-cols-2 bg-black/20 backdrop-blur-lg border border-gray-600/30">
                <TabsTrigger value="content" className="data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-300">Content</TabsTrigger>
                <TabsTrigger value="visuals" className="data-[state=active]:bg-pink-400/20 data-[state=active]:text-pink-300">Visuals</TabsTrigger>
              </TabsList>


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
                  {Object.keys(safelyGet(results, 'content', {})).length > 0 ? (
                    <Tabs
                      defaultValue={Object.keys(safelyGet(results, 'content', {}))[0] || "instagram"}
                      className="w-full"
                    >
                    <TabsList className="grid w-full mb-4" style={{ gridTemplateColumns: `repeat(${Math.min(Object.keys(safelyGet(results, 'content', {})).length, 5)}, minmax(0, 1fr))` }}>
                      {Object.entries(safelyGet(results, 'content', {})).map(([platform]) => {
                        const Icon =
                          platformIcons[platform as keyof typeof platformIcons] || Instagram;
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
                    {Object.entries(safelyGet(results, 'content', {})).map(
                      ([platform, content]: [string, any]) => (
                        <TabsContent key={platform} value={platform}>
                          <div className="space-y-4">
                            <div className="bg-gray-50 rounded-lg p-4">
                              <div className="flex justify-between items-start mb-3">
                                <h4 className="font-medium">Post Content</h4>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() =>
                                    handleCopyContent(safelyGet(content, 'text', ''), platform)
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
                                {safelyGet(content, 'text', 'No content available')}
                              </p>
                              <p className="text-sm text-gray-500 mt-2">
                                {safelyGet(content, 'character_count', 0)} characters
                              </p>
                            </div>
                            <div>
                              <h4 className="font-medium mb-2">Hashtags</h4>
                              <div className="flex flex-wrap gap-2">
                                {safelyGet(content, 'hashtags', []).map((tag: string, index: number) => (
                                  <Badge key={index} variant="secondary">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            {safelyGet(content, 'viral_elements', null) && (
                              <div>
                                <h4 className="font-medium mb-2">
                                  Viral Elements
                                </h4>
                                <div className="grid grid-cols-2 gap-2">
                                  {safelyGet(content, 'viral_elements', []).map(
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
                  ) : (
                    <div className="p-6 bg-gray-100 rounded-lg text-center">
                      <p className="text-gray-600 mb-2">No content available yet.</p>
                      <p className="text-sm text-gray-500">Content generation may still be in progress or failed to complete.</p>
                    </div>
                  )}
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
                        {safelyGet(results, 'visuals.recommended_style', 'Professional style with modern aesthetics')}
                      </p>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2 text-white">Color Palette</h3>
                      <div className="flex flex-wrap gap-3">
                        {(safelyGet(results, 'visuals.color_palette', []).length > 0 
                          ? safelyGet(results, 'visuals.color_palette', [])
                          : ['#f472b6', '#fbbf24', '#3b82f6', '#22c55e', '#8b5cf6', '#ef4444'] // Default brand colors
                        ).map((color: string, index: number) => (
                          <motion.div
                            key={index}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="group relative"
                          >
                            <div
                              className="w-20 h-20 rounded-xl shadow-lg flex items-center justify-center text-xs font-mono cursor-pointer hover:scale-110 transition-transform duration-300 border-2 border-white/20"
                              style={{ backgroundColor: color }}
                              onClick={() => navigator.clipboard.writeText(color)}
                              title={`Click to copy ${color}`}
                            >
                              <span className="bg-black/60 text-white px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                                {color}
                              </span>
                            </div>
                            <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                              Click to copy
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-4">
                        Curated Images (
                        {safelyGet(results, 'visuals.image_suggestions', []).length})
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {safelyGet(results, 'visuals.image_suggestions', []).map(
                          (image: any, index: number) => (
                            <motion.div
                              key={safelyGet(image, 'id', `img_${index}`)}
                              initial={{ opacity: 0, scale: 0.9 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{
                                duration: 0.3,
                                delay: index * 0.05,
                              }}
                              className="group relative rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-shadow"
                            >
                              <img
                                src={(() => {
                                  const imageUrl = safelyGet(image, 'url', '') || safelyGet(image, 'unsplash_url', '');
                                  if (!imageUrl) return 'https://via.placeholder.com/400x300/374151/ffffff?text=No+Image';
                                  
                                  // Add optimization parameters for faster loading
                                  if (imageUrl.includes('unsplash.com')) {
                                    const separator = imageUrl.includes('?') ? '&' : '?';
                                    return `${imageUrl}${separator}w=400&h=300&fit=crop&auto=format&q=80`;
                                  }
                                  return imageUrl;
                                })()}
                                alt={safelyGet(image, 'alt_description', '') || safelyGet(image, 'description', 'Campaign Image')}
                                className="w-full h-48 object-cover transition-all duration-200"
                                loading="eager"
                                decoding="async"
                                fetchPriority="high"
                                onLoad={(e) => {
                                  e.currentTarget.style.opacity = '1';
                                  e.currentTarget.style.filter = 'blur(0px)';
                                  console.log('Image loaded successfully:', e.currentTarget.src);
                                }}
                                onError={(e) => {
                                  console.error('Image failed to load:', e.currentTarget.src);
                                  e.currentTarget.src = 'https://via.placeholder.com/400x300/374151/ffffff?text=Image+Unavailable';
                                  e.currentTarget.style.opacity = '1';
                                  e.currentTarget.style.filter = 'blur(0px)';
                                }}
                                style={{ 
                                  opacity: 0,
                                  filter: 'blur(5px)',
                                  transition: 'opacity 0.2s ease-in-out, filter 0.2s ease-in-out'
                                }}
                              />
                              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                                <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
                                  <p className="text-sm font-medium truncate">
                                    {safelyGet(image, 'description', 'Image')}
                                  </p>
                                  <div className="flex items-center justify-between mt-1">
                                    <a
                                      href={safelyGet(image, 'photographer_url', '#')}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs hover:underline"
                                    >
                                      by {safelyGet(image, 'photographer', 'Unknown')}
                                    </a>
                                    <div className="flex items-center gap-1 text-xs">
                                      <Heart className="h-3 w-3" />
                                      {safelyGet(image, 'likes', 0)}
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

          </Tabs>
          </motion.div>


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
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
