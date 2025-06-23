import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { GradientBackground } from "@/components/ui/gradient-bg";
import { Sparkles as SparklesComponent } from "@/components/ui/sparkles";
import { AnimatedGridPattern } from "@/components/ui/grid-pattern";
import { Meteors } from "@/components/ui/meteors";
import { AgentProgressCard } from "@/components/dashboard/AgentProgressCard";
import {
  useCampaignStatus,
  useForceCompleteCampaign,
} from "@/hooks/useCampaign";
import {
  ArrowLeft,
  CheckCircle,
  Clock,
  Loader2,
  XCircle,
  Eye,
  Zap,
  AlertCircle,
  Rocket,
  Brain,
  Activity,
  Sparkles,
} from "lucide-react";

export function CampaignDashboard() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: campaign, isLoading, error } = useCampaignStatus(id);
  const forceComplete = useForceCompleteCampaign();

  useEffect(() => {
    if (campaign?.status === "completed") {
      // Redirect to results after a short delay when campaign completes
      const timer = setTimeout(() => {
        navigate(`/campaign/${id}/results`);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [campaign?.status, id, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center relative overflow-hidden">
        <GradientBackground />
        <SparklesComponent 
          className="opacity-30" 
          particleColor="#f472b6" 
          particleDensity={40}
        />
        <AnimatedGridPattern 
          width={80} 
          height={80} 
          className="opacity-10"
          maxOpacity={0.15}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center relative z-10"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 mx-auto mb-6"
          >
            <Brain className="w-16 h-16 text-pink-400" />
          </motion.div>
          <h2 className="text-2xl font-bold text-white mb-2">AI Campaign Processing</h2>
          <p className="text-gray-300">Loading campaign status...</p>
        </motion.div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center relative overflow-hidden">
        <GradientBackground />
        <SparklesComponent 
          className="opacity-20" 
          particleColor="#f472b6" 
          particleDensity={30}
        />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative z-10"
        >
          <Card className="max-w-md bg-black/20 backdrop-blur-lg border border-gray-600/30">
            <CardContent className="pt-6 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <XCircle className="h-16 w-16 text-red-400 mx-auto mb-4" />
              </motion.div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Campaign Not Found
              </h2>
              <p className="text-gray-300 mb-6">
                We couldn't find this campaign. It may have been deleted or doesn't exist.
              </p>
              <Button 
                onClick={() => navigate("/")} 
                className="w-full bg-gradient-to-r from-pink-500 to-amber-500 text-white border-0 hover:from-pink-600 hover:to-amber-600"
              >
                Go to Home
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (campaign.status) {
      case "processing":
        return <Loader2 className="h-5 w-5 animate-spin" />;
      case "completed":
        return <CheckCircle className="h-5 w-5" />;
      case "failed":
        return <XCircle className="h-5 w-5" />;
      default:
        return <Clock className="h-5 w-5" />;
    }
  };

  const getStatusVariant = () => {
    switch (campaign.status) {
      case "processing":
        return "running";
      case "completed":
        return "completed";
      case "failed":
        return "error";
      default:
        return "default";
    }
  };

  const handleForceComplete = async () => {
    if (id) {
      try {
        await forceComplete.mutateAsync(id);
      } catch (error) {
        console.error("Failed to force complete:", error);
      }
    }
  };

  const completedAgents = campaign.agent_progress.filter(
    (agent) => agent.status === "completed"
  ).length;
  const totalProgress = Math.round(
    (completedAgents / campaign.agent_progress.length) * 100
  );

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Enhanced Background */}
      <GradientBackground />
      <SparklesComponent 
        className="opacity-40" 
        particleColor="#f472b6" 
        particleDensity={60}
      />
      <Meteors number={8} />
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
                onClick={() => navigate("/create")}
                className="text-gray-300 hover:text-white hover:bg-white/10"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Create
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center gap-3">
                <img 
                  src="/vyralflow.png" 
                  alt="VyralFlow AI Logo" 
                  className="w-8 h-8 object-contain"
                />
                <span className="text-xl font-bold text-white">Campaign Dashboard</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <Badge 
                variant={getStatusVariant()}
                className="text-base py-2 px-4 bg-black/30 border-pink-400/30"
              >
                {getStatusIcon()}
                <span className="ml-2">
                  {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                </span>
              </Badge>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 relative z-10 max-w-6xl">
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
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-black/40 backdrop-blur-lg border border-pink-500/30 mb-6"
            >
              <Brain className="w-5 h-5 text-pink-400" />
              <span className="text-sm font-medium text-white">
                AI Agents at Work
              </span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </motion.div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              Campaign in Progress
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Watch as our specialized AI agents collaborate to create your viral campaign
            </p>
          </motion.div>

          {/* Campaign Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-8"
          >
            <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden">
              {/* Card effects */}
              <div className="absolute inset-0 opacity-20">
                <SparklesComponent 
                  particleColor="#f472b6" 
                  particleDensity={15}
                  minSize={1}
                  maxSize={3}
                />
              </div>
              
              <CardHeader className="relative z-10">
                <CardTitle className="text-2xl font-bold text-white flex items-center gap-3">
                  <Rocket className="w-7 h-7 text-pink-400" />
                  Campaign Overview
                </CardTitle>
                <CardDescription className="text-gray-300">
                  ID: {campaign.campaign_id} • Created: {new Date(campaign.created_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="relative z-10 space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-3">
                    <span className="text-gray-300">Overall Progress</span>
                    <span className="font-bold text-white text-lg">{totalProgress}%</span>
                  </div>
                  <div className="relative">
                    <Progress value={totalProgress} className="h-4" />
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-pink-500/20 to-amber-500/20 rounded-full"
                      animate={{ opacity: [0.3, 0.6, 0.3] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="text-gray-300">
                    <span className="font-semibold text-white">{completedAgents}</span> of <span className="font-semibold text-white">{campaign.agent_progress.length}</span> agents completed
                  </div>
                  {campaign.status === "completed" && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 200 }}
                    >
                      <Button
                        onClick={() => navigate(`/campaign/${id}/results`)}
                        className="bg-gradient-to-r from-pink-500 to-amber-500 text-white border-0 hover:from-pink-600 hover:to-amber-600 gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        View Results
                      </Button>
                    </motion.div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Agent Progress Cards */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mb-8"
          >
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black/20 backdrop-blur-lg border border-pink-500/30 mb-4"
              >
                <Sparkles className="w-5 h-5 text-pink-400" />
                <span className="text-sm font-medium text-white">
                  AI Agent Progress
                </span>
              </motion.div>
              <h2 className="text-3xl font-bold text-white mb-2">Specialized AI Agents</h2>
              <p className="text-gray-300">Each agent contributes unique capabilities to your campaign</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              {campaign.agent_progress.map((agent, index) => (
                <motion.div
                  key={agent.agent_name}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                >
                  <AgentProgressCard agent={agent} />
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Demo Controls (for hackathon) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 relative overflow-hidden">
              <div className="absolute inset-0 opacity-10">
                <SparklesComponent 
                  particleColor="#fbbf24" 
                  particleDensity={10}
                  minSize={1}
                  maxSize={2}
                />
              </div>
              
              <CardHeader className="relative z-10">
                <CardTitle className="flex items-center gap-2 text-white">
                  <AlertCircle className="h-5 w-5 text-yellow-400" />
                  Demo Controls
                </CardTitle>
                <CardDescription className="text-gray-300">For demonstration purposes only</CardDescription>
              </CardHeader>
              <CardContent className="relative z-10">
                <div className="flex items-center justify-between">
                  <p className="text-gray-300">
                    If the campaign is taking too long, you can force complete it for demo purposes.
                  </p>
                  <Button
                    variant="outline"
                    onClick={handleForceComplete}
                    disabled={
                      campaign.status !== "processing" || forceComplete.isPending
                    }
                    className="border-yellow-400 text-yellow-400 hover:bg-yellow-400/10 gap-2"
                  >
                    <Zap className="w-4 h-4" />
                    {forceComplete.isPending ? "Completing..." : "Force Complete"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Success Message */}
          <AnimatePresence>
            {campaign.status === "completed" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.6, type: "spring", stiffness: 200 }}
                className="fixed inset-0 flex items-center justify-center pointer-events-none z-50"
              >
                <motion.div
                  initial={{ y: 20 }}
                  animate={{ y: 0 }}
                  className="bg-black/80 backdrop-blur-lg rounded-2xl border border-green-400/30 pointer-events-auto relative overflow-hidden"
                >
                  <div className="absolute inset-0 opacity-30">
                    <SparklesComponent 
                      particleColor="#22c55e" 
                      particleDensity={50}
                      minSize={2}
                      maxSize={4}
                    />
                  </div>
                  
                  <div className="relative z-10 p-8 text-center">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, type: "spring", stiffness: 300 }}
                    >
                      <CheckCircle className="h-20 w-20 text-green-400 mx-auto mb-6" />
                    </motion.div>
                    <h2 className="text-3xl font-bold text-white mb-3">
                      Campaign Complete!
                    </h2>
                    <p className="text-gray-300 text-lg">
                      Redirecting to results...
                    </p>
                    <motion.div
                      className="w-32 h-1 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full mx-auto mt-4"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ duration: 2 }}
                    />
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
