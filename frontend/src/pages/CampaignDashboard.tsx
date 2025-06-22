import { useEffect } from "react";
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading campaign status...</p>
        </div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-center mb-2">
              Campaign Not Found
            </h2>
            <p className="text-gray-600 text-center mb-4">
              We couldn't find this campaign. It may have been deleted or
              doesn't exist.
            </p>
            <Button onClick={() => navigate("/")} className="w-full">
              Go to Home
            </Button>
          </CardContent>
        </Card>
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <div className="mb-8">
            <Button
              variant="ghost"
              onClick={() => navigate("/create")}
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Create
            </Button>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold mb-2">Campaign Progress</h1>
                <p className="text-gray-600">
                  Watch as our AI agents work together to create your viral
                  campaign
                </p>
              </div>
              <Badge
                variant={getStatusVariant()}
                className="text-base py-2 px-4"
              >
                {getStatusIcon()}
                <span className="ml-2">
                  {campaign.status.charAt(0).toUpperCase() +
                    campaign.status.slice(1)}
                </span>
              </Badge>
            </div>
          </div>

          {/* Campaign Overview */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Campaign Overview</CardTitle>
              <CardDescription>
                ID: {campaign.campaign_id} • Created:{" "}
                {new Date(campaign.created_at).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Overall Progress</span>
                    <span className="font-medium">{totalProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <motion.div
                      className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${totalProgress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    {completedAgents} of {campaign.agent_progress.length} agents
                    completed
                  </div>
                  {campaign.status === "completed" && (
                    <Button
                      variant="gradient"
                      onClick={() => navigate(`/campaign/${id}/results`)}
                      className="gap-2"
                    >
                      <Eye className="w-4 h-4" />
                      View Results
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Agent Progress Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {campaign.agent_progress.map((agent, index) => (
              <motion.div
                key={agent.agent_name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <AgentProgressCard agent={agent} />
              </motion.div>
            ))}
          </div>

          {/* Demo Controls (for hackathon) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
                Demo Controls
              </CardTitle>
              <CardDescription>For demonstration purposes only</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  If the campaign is taking too long, you can force complete it
                  for demo purposes.
                </p>
                <Button
                  variant="outline"
                  onClick={handleForceComplete}
                  disabled={
                    campaign.status !== "processing" || forceComplete.isPending
                  }
                  className="gap-2"
                >
                  <Zap className="w-4 h-4" />
                  {forceComplete.isPending ? "Completing..." : "Force Complete"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Success Message */}
          {campaign.status === "completed" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="fixed inset-0 flex items-center justify-center pointer-events-none z-50"
            >
              <Card className="bg-green-50 border-green-200 pointer-events-auto">
                <CardContent className="pt-6">
                  <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-center mb-2">
                    Campaign Complete!
                  </h2>
                  <p className="text-gray-600 text-center">
                    Redirecting to results...
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
