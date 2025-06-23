import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { GradientBackground } from "@/components/ui/gradient-bg";
import { Sparkles as SparklesComponent } from "@/components/ui/sparkles";
import { AnimatedGridPattern } from "@/components/ui/grid-pattern";
import { Meteors } from "@/components/ui/meteors";
import { useCreateCampaign } from "@/hooks/useCampaign";
import type { CampaignRequest } from "@/types/campaign";
import {
  ArrowLeft,
  ArrowRight,
  Building,
  Target,
  MessageSquare,
  Sparkles,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  CheckCircle,
  Zap,
  Wand2,
  Brain,
  Rocket,
} from "lucide-react";

const platforms = [
  {
    id: "instagram",
    name: "Instagram",
    icon: Instagram,
    color: "text-pink-600",
    description: "Visual storytelling with high engagement",
  },
  { 
    id: "facebook", 
    name: "Facebook", 
    icon: Facebook, 
    color: "text-blue-600",
    description: "Community building and sharing"
  },
  { 
    id: "linkedin", 
    name: "LinkedIn", 
    icon: Linkedin, 
    color: "text-blue-700",
    description: "Professional networking and B2B"
  },
  { 
    id: "twitter", 
    name: "Twitter", 
    icon: Twitter, 
    color: "text-blue-400",
    description: "Real-time conversations and trends"
  },
];

const industries = [
  "Technology", "Healthcare", "Finance", "E-commerce", "Education", 
  "Food & Beverage", "Fashion", "Real Estate", "Entertainment", 
  "Travel", "Sports", "Beauty", "Automotive", "Other"
];

const brandVoices = [
  { value: "professional", label: "Professional", description: "Formal and authoritative" },
  { value: "friendly", label: "Friendly", description: "Warm and approachable" },
  { value: "casual", label: "Casual", description: "Relaxed and conversational" },
  { value: "humorous", label: "Humorous", description: "Fun and entertaining" },
  { value: "inspirational", label: "Inspirational", description: "Motivating and uplifting" },
];

const steps = [
  {
    id: 1,
    title: "Business Details",
    description: "Tell us about your brand",
    icon: Building,
  },
  {
    id: 2,
    title: "Campaign Goals",
    description: "Define your objectives",
    icon: Target,
  },
  {
    id: 3,
    title: "Platform Selection",
    description: "Choose your channels",
    icon: MessageSquare,
  },
  {
    id: 4,
    title: "Final Details",
    description: "Complete your setup",
    icon: Sparkles,
  },
];

export function CampaignCreate() {
  const navigate = useNavigate();
  const createCampaign = useCreateCampaign();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Partial<CampaignRequest>>({
    target_platforms: [],
    keywords: [],
  });

  const [keywords, setKeywords] = useState("");

  const handleInputChange = (field: keyof CampaignRequest, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePlatformToggle = (platformId: string) => {
    const currentPlatforms = formData.target_platforms || [];
    const updatedPlatforms = currentPlatforms.includes(platformId)
      ? currentPlatforms.filter((p) => p !== platformId)
      : [...currentPlatforms, platformId];
    
    handleInputChange("target_platforms", updatedPlatforms);
  };

  const addKeyword = () => {
    if (keywords.trim() && formData.keywords) {
      const newKeywords = [...formData.keywords, keywords.trim()];
      handleInputChange("keywords", newKeywords);
      setKeywords("");
    }
  };

  const removeKeyword = (index: number) => {
    if (formData.keywords) {
      const newKeywords = formData.keywords.filter((_, i) => i !== index);
      handleInputChange("keywords", newKeywords);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.business_name && formData.industry;
      case 2:
        return formData.campaign_goal;
      case 3:
        return formData.target_platforms && formData.target_platforms.length > 0;
      case 4:
        return formData.brand_voice;
      default:
        return false;
    }
  };

  const handleSubmit = async () => {
    if (!isFormValid()) return;

    try {
      const result = await createCampaign.mutateAsync(formData as CampaignRequest);
      navigate(`/campaign/${result.campaign_id}`);
    } catch (error) {
      console.error("Failed to create campaign:", error);
    }
  };

  const isFormValid = () => {
    return (
      formData.business_name &&
      formData.industry &&
      formData.campaign_goal &&
      formData.target_platforms &&
      formData.target_platforms.length > 0 &&
      formData.brand_voice
    );
  };

  const getStepIcon = (step: number) => {
    const stepData = steps.find(s => s.id === step);
    return stepData ? stepData.icon : Building;
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Enhanced Background */}
      <GradientBackground />
      <SparklesComponent 
        className="opacity-40" 
        particleColor="#f472b6" 
        particleDensity={60}
      />
      <Meteors number={10} />
      <AnimatedGridPattern 
        width={100} 
        height={100} 
        className="opacity-10"
        maxOpacity={0.15}
      />

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
                onClick={() => navigate("/")}
                className="text-gray-300 hover:text-white hover:bg-white/10"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center gap-3">
                <img 
                  src="/vyralflow.png" 
                  alt="VyralFlow AI Logo" 
                  className="w-8 h-8 object-contain"
                />
                <span className="text-xl font-bold text-white">Create Campaign</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <Badge variant="secondary" className="bg-black/30 text-white border-pink-400/30">
                Step {currentStep} of 4
              </Badge>
              <div className="w-32">
                <Progress value={(currentStep / 4) * 100} className="h-2" />
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Step Indicator */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center mb-12"
          >
            <div className="flex items-center gap-4">
              {steps.map((step, index) => {
                const StepIcon = step.icon;
                const isActive = currentStep === step.id;
                const isCompleted = currentStep > step.id;
                
                return (
                  <div key={step.id} className="flex items-center">
                    <motion.div
                      className={`relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 ${
                        isActive
                          ? "border-pink-400 bg-pink-400/20"
                          : isCompleted
                          ? "border-green-400 bg-green-400/20"
                          : "border-gray-600 bg-gray-800/50"
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {isCompleted ? (
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      ) : (
                        <StepIcon className={`w-6 h-6 ${
                          isActive ? "text-pink-400" : "text-gray-400"
                        }`} />
                      )}
                      
                      {isActive && (
                        <motion.div
                          className="absolute inset-0 rounded-full border-2 border-pink-400"
                          initial={{ scale: 1, opacity: 1 }}
                          animate={{ scale: 1.3, opacity: 0 }}
                          transition={{ duration: 2, repeat: Infinity }}
                        />
                      )}
                    </motion.div>
                    
                    {index < steps.length - 1 && (
                      <div className={`w-16 h-0.5 mx-2 ${
                        currentStep > step.id ? "bg-green-400" : "bg-gray-600"
                      }`} />
                    )}
                  </div>
                );
              })}
            </div>
          </motion.div>

          {/* Form Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden">
                {/* Card effects */}
                <div className="absolute inset-0 opacity-20">
                  <SparklesComponent 
                    particleColor="#f472b6" 
                    particleDensity={20}
                    minSize={1}
                    maxSize={3}
                  />
                </div>
                
                <CardHeader className="relative z-10">
                  <CardTitle className="text-2xl font-bold text-white flex items-center gap-3">
                    {React.createElement(getStepIcon(currentStep), { 
                      className: "w-8 h-8 text-pink-400" 
                    })}
                    {steps.find(s => s.id === currentStep)?.title}
                  </CardTitle>
                  <CardDescription className="text-gray-300">
                    {steps.find(s => s.id === currentStep)?.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="relative z-10 space-y-6">
                  {/* Step 1: Business Details */}
                  {currentStep === 1 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="business_name" className="text-white">
                            Business Name *
                          </Label>
                          <Input
                            id="business_name"
                            placeholder="Enter your business name"
                            value={formData.business_name || ""}
                            onChange={(e) => handleInputChange("business_name", e.target.value)}
                            className="bg-black/20 border-gray-600 text-white placeholder:text-gray-400 focus:border-pink-400"
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="industry" className="text-white">
                            Industry *
                          </Label>
                          <Select
                            value={formData.industry || ""}
                            onValueChange={(value) => handleInputChange("industry", value)}
                          >
                            <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                              <SelectValue placeholder="Select your industry" />
                            </SelectTrigger>
                            <SelectContent>
                              {industries.map((industry) => (
                                <SelectItem key={industry} value={industry}>
                                  {industry}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="target_audience" className="text-white">
                          Target Audience
                        </Label>
                        <Input
                          id="target_audience"
                          placeholder="Describe your target audience (optional)"
                          value={formData.target_audience || ""}
                          onChange={(e) => handleInputChange("target_audience", e.target.value)}
                          className="bg-black/20 border-gray-600 text-white placeholder:text-gray-400 focus:border-pink-400"
                        />
                      </div>
                    </motion.div>
                  )}

                  {/* Step 2: Campaign Goals */}
                  {currentStep === 2 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      <div className="space-y-2">
                        <Label htmlFor="campaign_goal" className="text-white">
                          Campaign Goal *
                        </Label>
                        <Textarea
                          id="campaign_goal"
                          placeholder="Describe what you want to achieve with this campaign..."
                          value={formData.campaign_goal || ""}
                          onChange={(e) => handleInputChange("campaign_goal", e.target.value)}
                          className="bg-black/20 border-gray-600 text-white placeholder:text-gray-400 focus:border-pink-400 min-h-[120px]"
                        />
                      </div>

                      <div className="space-y-4">
                        <Label className="text-white">Keywords (Optional)</Label>
                        <div className="flex gap-2">
                          <Input
                            placeholder="Add a keyword"
                            value={keywords}
                            onChange={(e) => setKeywords(e.target.value)}
                            onKeyPress={(e) => e.key === "Enter" && addKeyword()}
                            className="bg-black/20 border-gray-600 text-white placeholder:text-gray-400 focus:border-pink-400"
                          />
                          <Button
                            type="button"
                            onClick={addKeyword}
                            variant="outline"
                            className="border-pink-400 text-pink-400 hover:bg-pink-400/10"
                          >
                            Add
                          </Button>
                        </div>
                        
                        {formData.keywords && formData.keywords.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {formData.keywords.map((keyword, index) => (
                              <Badge
                                key={index}
                                variant="secondary"
                                className="bg-pink-400/20 text-pink-300 border-pink-400/30"
                              >
                                {keyword}
                                <button
                                  onClick={() => removeKeyword(index)}
                                  className="ml-2 text-pink-300 hover:text-white"
                                >
                                  ×
                                </button>
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {/* Step 3: Platform Selection */}
                  {currentStep === 3 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      <div className="space-y-4">
                        <Label className="text-white">Select Target Platforms *</Label>
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {platforms.map((platform) => {
                            const Icon = platform.icon;
                            const isSelected = formData.target_platforms?.includes(platform.id);
                            
                            return (
                              <motion.div
                                key={platform.id}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className={`relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-300 ${
                                  isSelected
                                    ? "border-pink-400 bg-pink-400/10"
                                    : "border-gray-600 bg-black/20 hover:border-gray-500"
                                }`}
                                onClick={() => handlePlatformToggle(platform.id)}
                              >
                                <div className="flex items-start gap-3">
                                  <div className={`p-2 rounded-lg ${
                                    isSelected ? "bg-pink-400/20" : "bg-gray-700/50"
                                  }`}>
                                    <Icon className={`w-6 h-6 ${
                                      isSelected ? "text-pink-400" : platform.color
                                    }`} />
                                  </div>
                                  
                                  <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                      <h3 className="font-semibold text-white">
                                        {platform.name}
                                      </h3>
                                      <Checkbox checked={isSelected} />
                                    </div>
                                    <p className="text-sm text-gray-400 mt-1">
                                      {platform.description}
                                    </p>
                                  </div>
                                </div>
                                
                                {isSelected && (
                                  <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="absolute top-2 right-2"
                                  >
                                    <CheckCircle className="w-5 h-5 text-pink-400" />
                                  </motion.div>
                                )}
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* Step 4: Final Details */}
                  {currentStep === 4 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      <div className="space-y-4">
                        <Label className="text-white">Brand Voice *</Label>
                        <div className="grid md:grid-cols-2 gap-4">
                          {brandVoices.map((voice) => {
                            const isSelected = formData.brand_voice === voice.value;
                            
                            return (
                              <motion.div
                                key={voice.value}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-300 ${
                                  isSelected
                                    ? "border-pink-400 bg-pink-400/10"
                                    : "border-gray-600 bg-black/20 hover:border-gray-500"
                                }`}
                                onClick={() => handleInputChange("brand_voice", voice.value)}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <h3 className="font-semibold text-white">
                                      {voice.label}
                                    </h3>
                                    <p className="text-sm text-gray-400">
                                      {voice.description}
                                    </p>
                                  </div>
                                  <Checkbox checked={isSelected} />
                                </div>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Summary */}
                      <div className="space-y-4 p-6 bg-black/30 rounded-lg border border-gray-600/30">
                        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                          <Zap className="w-5 h-5 text-pink-400" />
                          Campaign Summary
                        </h3>
                        <div className="grid md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-400">Business:</span>
                            <span className="text-white ml-2">{formData.business_name}</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Industry:</span>
                            <span className="text-white ml-2">{formData.industry}</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Platforms:</span>
                            <span className="text-white ml-2">{formData.target_platforms?.length} selected</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Voice:</span>
                            <span className="text-white ml-2">{formData.brand_voice}</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-between items-center mt-8"
          >
            <Button
              variant="outline"
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
              className="border-gray-600 text-gray-300 hover:bg-gray-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            <div className="flex gap-3">
              {currentStep < 4 ? (
                <Button
                  onClick={() => setCurrentStep(currentStep + 1)}
                  disabled={!canProceed()}
                  className="bg-gradient-to-r from-pink-500 to-amber-500 text-white border-0 hover:from-pink-600 hover:to-amber-600"
                >
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={!isFormValid() || createCampaign.isPending}
                  className="bg-gradient-to-r from-pink-500 to-amber-500 text-white border-0 hover:from-pink-600 hover:to-amber-600"
                >
                  {createCampaign.isPending ? (
                    <>
                      <Brain className="w-4 h-4 mr-2 animate-pulse" />
                      Creating Campaign...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4 mr-2" />
                      Create Campaign
                    </>
                  )}
                </Button>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}