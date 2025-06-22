import { motion } from "framer-motion";
import {
  TrendingUp,
  Edit3,
  Image,
  Calendar,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { AgentProgress } from "@/types/campaign";

interface AgentProgressCardProps {
  agent: AgentProgress;
}

const agentIcons = {
  trend_analyzer: TrendingUp,
  content_writer: Edit3,
  visual_designer: Image,
  campaign_scheduler: Calendar,
};

const agentDescriptions = {
  trend_analyzer: "Analyzing viral trends and market insights",
  content_writer: "Creating engaging platform-specific content",
  visual_designer: "Curating professional visual assets",
  campaign_scheduler: "Optimizing posting schedule for maximum reach",
};

const statusIcons = {
  pending: Clock,
  running: Loader2,
  completed: CheckCircle,
  error: XCircle,
};

export function AgentProgressCard({ agent }: AgentProgressCardProps) {
  const Icon = agentIcons[agent.agent_name];
  const StatusIcon = statusIcons[agent.status];
  const description = agentDescriptions[agent.agent_name];

  const getStatusVariant = (status: AgentProgress["status"]) => {
    switch (status) {
      case "pending":
        return "pending";
      case "running":
        return "running";
      case "completed":
        return "completed";
      case "error":
        return "error";
      default:
        return "default";
    }
  };

  const getProgressColor = (status: AgentProgress["status"]) => {
    switch (status) {
      case "pending":
        return "bg-gray-400";
      case "running":
        return "bg-blue-500";
      case "completed":
        return "bg-green-500";
      case "error":
        return "bg-red-500";
      default:
        return "bg-gray-400";
    }
  };

  const formatAgentName = (name: string) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div
                className={`p-2 rounded-lg ${
                  agent.status === "completed"
                    ? "bg-green-100"
                    : agent.status === "running"
                    ? "bg-blue-100"
                    : agent.status === "error"
                    ? "bg-red-100"
                    : "bg-gray-100"
                }`}
              >
                <Icon
                  className={`h-5 w-5 ${
                    agent.status === "completed"
                      ? "text-green-600"
                      : agent.status === "running"
                      ? "text-blue-600"
                      : agent.status === "error"
                      ? "text-red-600"
                      : "text-gray-600"
                  }`}
                />
              </div>
              <div>
                <CardTitle className="text-lg">
                  {formatAgentName(agent.agent_name)}
                </CardTitle>
                <CardDescription className="text-sm">
                  {description}
                </CardDescription>
              </div>
            </div>
            <Badge variant={getStatusVariant(agent.status)} className="ml-auto">
              <StatusIcon
                className={`h-3 w-3 mr-1 ${
                  agent.status === "running" ? "animate-spin" : ""
                }`}
              />
              {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <Progress
            value={agent.progress_percentage}
            className="h-2"
            indicatorClassName={getProgressColor(agent.status)}
          />
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{agent.message}</span>
            <span className="font-medium">{agent.progress_percentage}%</span>
          </div>
          {agent.ai_generated && (
            <div className="flex items-center text-xs text-muted-foreground">
              <span className="mr-1">✨</span>
              AI-powered generation
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
