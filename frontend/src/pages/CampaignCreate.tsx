import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
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
import { useCreateCampaign } from "@/hooks/useCampaign";
import type { CampaignRequest } from "@/types/campaign";
import {
  ArrowLeft,
  ArrowRight,
  Building,
  Target,
  MessageSquare,
  Users,
  DollarSign,
  Sparkles,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  Music2,
} from "lucide-react";

const platforms = [
  {
    id: "instagram",
    name: "Instagram",
    icon: Instagram,
    color: "text-pink-600",
  },
  { id: "tiktok", name: "TikTok", icon: Music2, color: "text-gray-900" },
  { id: "facebook", name: "Facebook", icon: Facebook, color: "text-blue-600" },
  { id: "linkedin", name: "LinkedIn", icon: Linkedin, color: "text-blue-700" },
  { id: "twitter", name: "Twitter", icon: Twitter, color: "text-blue-400" },
];

const industries = [
  "Technology",
  "Fashion & Retail",
  "Health & Wellness",
  "Food & Beverage",
  "Travel & Tourism",
  "Education",
  "Finance",
  "Entertainment",
  "Real Estate",
  "Other",
];

const brandVoices = [
  {
    value: "professional",
    label: "Professional",
    description: "Formal and business-oriented",
  },
  {
    value: "casual",
    label: "Casual",
    description: "Friendly and conversational",
  },
  { value: "playful", label: "Playful", description: "Fun and energetic" },
  {
    value: "authoritative",
    label: "Authoritative",
    description: "Expert and confident",
  },
];

export function CampaignCreate() {
  const navigate = useNavigate();
  const createCampaign = useCreateCampaign();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Partial<CampaignRequest>>({
    business_name: "",
    industry: "",
    campaign_goal: "",
    target_platforms: [],
    brand_voice: "professional",
    target_audience: "",
    keywords: [],
    budget_range: "medium",
  });

  const handleInputChange = (field: keyof CampaignRequest, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const handlePlatformToggle = (platformId: string) => {
    const platforms = formData.target_platforms || [];
    if (platforms.includes(platformId)) {
      handleInputChange(
        "target_platforms",
        platforms.filter((p) => p !== platformId)
      );
    } else {
      handleInputChange("target_platforms", [...platforms, platformId]);
    }
  };

  const handleKeywordInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && e.currentTarget.value.trim()) {
      e.preventDefault();
      const keywords = formData.keywords || [];
      handleInputChange("keywords", [
        ...keywords,
        e.currentTarget.value.trim(),
      ]);
      e.currentTarget.value = "";
    }
  };

  const removeKeyword = (index: number) => {
    const keywords = formData.keywords || [];
    handleInputChange(
      "keywords",
      keywords.filter((_, i) => i !== index)
    );
  };

  const handleSubmit = async () => {
    try {
      const result = await createCampaign.mutateAsync(
        formData as CampaignRequest
      );
      navigate(`/campaign/${result.campaign_id}`);
    } catch (error) {
      console.error("Failed to create campaign:", error);
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return (
          formData.business_name && formData.industry && formData.campaign_goal
        );
      case 2:
        return (
          (formData.target_platforms?.length || 0) > 0 && formData.brand_voice
        );
      case 3:
        return true; // Optional fields
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8">
            <Button
              variant="ghost"
              onClick={() => navigate("/")}
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
            <h1 className="text-4xl font-bold mb-2">
              Create Your Viral Campaign
            </h1>
            <p className="text-gray-600">
              Let our AI agents craft the perfect campaign for your business
            </p>
          </div>

          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              {[1, 2, 3].map((step) => (
                <div key={step} className={`flex-1 ${step < 3 ? "mr-2" : ""}`}>
                  <div
                    className={`h-2 rounded-full transition-colors ${
                      step <= currentStep ? "bg-purple-600" : "bg-gray-200"
                    }`}
                  />
                </div>
              ))}
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Business Info</span>
              <span>Platform & Voice</span>
              <span>Additional Details</span>
            </div>
          </div>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle>
                {currentStep === 1 && "Tell us about your business"}
                {currentStep === 2 && "Choose platforms and voice"}
                {currentStep === 3 && "Additional details (optional)"}
              </CardTitle>
              <CardDescription>
                {currentStep === 1 &&
                  "This helps our AI understand your business context"}
                {currentStep === 2 &&
                  "Select where and how you want to communicate"}
                {currentStep === 3 &&
                  "Fine-tune your campaign for better results"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Step 1: Business Information */}
              {currentStep === 1 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6"
                >
                  <div>
                    <Label htmlFor="business_name">
                      Business Name <span className="text-red-500">*</span>
                    </Label>
                    <div className="relative mt-1">
                      <Building className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="business_name"
                        placeholder="Enter your business name"
                        value={formData.business_name}
                        onChange={(e) =>
                          handleInputChange("business_name", e.target.value)
                        }
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="industry">
                      Industry <span className="text-red-500">*</span>
                    </Label>
                    <Select
                      value={formData.industry}
                      onValueChange={(value) =>
                        handleInputChange("industry", value)
                      }
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select your industry" />
                      </SelectTrigger>
                      <SelectContent>
                        {industries.map((industry) => (
                          <SelectItem
                            key={industry}
                            value={industry.toLowerCase()}
                          >
                            {industry}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="campaign_goal">
                      Campaign Goal <span className="text-red-500">*</span>
                    </Label>
                    <div className="relative mt-1">
                      <Target className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Textarea
                        id="campaign_goal"
                        placeholder="Describe what you want to achieve with this campaign..."
                        value={formData.campaign_goal}
                        onChange={(e) =>
                          handleInputChange("campaign_goal", e.target.value)
                        }
                        className="pl-10 min-h-[100px]"
                      />
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Be specific about your objectives, target metrics, or
                      desired outcomes
                    </p>
                  </div>
                </motion.div>
              )}

              {/* Step 2: Platform & Voice */}
              {currentStep === 2 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6"
                >
                  <div>
                    <Label>
                      Target Platforms <span className="text-red-500">*</span>
                    </Label>
                    <p className="text-sm text-gray-500 mb-3">
                      Select all platforms where you want to run your campaign
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {platforms.map((platform) => (
                        <div
                          key={platform.id}
                          onClick={() => handlePlatformToggle(platform.id)}
                          className={`flex items-center space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                            formData.target_platforms?.includes(platform.id)
                              ? "border-purple-600 bg-purple-50"
                              : "border-gray-200 hover:border-gray-300"
                          }`}
                        >
                          <Checkbox
                            checked={formData.target_platforms?.includes(
                              platform.id
                            )}
                            onCheckedChange={() =>
                              handlePlatformToggle(platform.id)
                            }
                          />
                          <platform.icon
                            className={`h-5 w-5 ${platform.color}`}
                          />
                          <span className="text-sm font-medium">
                            {platform.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label>
                      Brand Voice <span className="text-red-500">*</span>
                    </Label>
                    <p className="text-sm text-gray-500 mb-3">
                      How should your brand communicate?
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {brandVoices.map((voice) => (
                        <div
                          key={voice.value}
                          onClick={() =>
                            handleInputChange("brand_voice", voice.value)
                          }
                          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                            formData.brand_voice === voice.value
                              ? "border-purple-600 bg-purple-50"
                              : "border-gray-200 hover:border-gray-300"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{voice.label}</span>
                            <MessageSquare className="h-4 w-4 text-gray-400" />
                          </div>
                          <p className="text-sm text-gray-600">
                            {voice.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 3: Additional Details */}
              {currentStep === 3 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6"
                >
                  <div>
                    <Label htmlFor="target_audience">Target Audience</Label>
                    <div className="relative mt-1">
                      <Users className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Textarea
                        id="target_audience"
                        placeholder="Describe your ideal customers (demographics, interests, behaviors)..."
                        value={formData.target_audience}
                        onChange={(e) =>
                          handleInputChange("target_audience", e.target.value)
                        }
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="keywords">Keywords</Label>
                    <p className="text-sm text-gray-500 mb-2">
                      Press Enter to add keywords that describe your campaign
                    </p>
                    <Input
                      id="keywords"
                      placeholder="Type a keyword and press Enter..."
                      onKeyDown={handleKeywordInput}
                    />
                    {formData.keywords && formData.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {formData.keywords.map((keyword, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="cursor-pointer"
                            onClick={() => removeKeyword(index)}
                          >
                            {keyword}
                            <span className="ml-1">×</span>
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="budget_range">Budget Range</Label>
                    <div className="relative mt-1">
                      <DollarSign className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Select
                        value={formData.budget_range}
                        onValueChange={(value) =>
                          handleInputChange("budget_range", value)
                        }
                      >
                        <SelectTrigger className="pl-10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">
                            Low (Under $1,000)
                          </SelectItem>
                          <SelectItem value="medium">
                            Medium ($1,000 - $5,000)
                          </SelectItem>
                          <SelectItem value="high">High ($5,000+)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentStep(currentStep - 1)}
              disabled={currentStep === 1}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            {currentStep < 3 ? (
              <Button
                onClick={() => setCurrentStep(currentStep + 1)}
                disabled={!isStepValid()}
              >
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button
                variant="gradient"
                onClick={handleSubmit}
                disabled={!isStepValid() || createCampaign.isPending}
              >
                {createCampaign.isPending ? (
                  <>
                    <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                    Creating Campaign...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Create Campaign
                  </>
                )}
              </Button>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
