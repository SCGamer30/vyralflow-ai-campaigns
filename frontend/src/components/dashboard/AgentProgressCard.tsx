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
  Sparkles,
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
import { Sparkles as SparklesComponent } from "@/components/ui/sparkles";
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
      whileHover={{ scale: 1.02 }}
      className="group"
    >
      <Card className="bg-black/20 backdrop-blur-lg border border-gray-600/30 overflow-hidden relative hover:border-pink-400/40 transition-all duration-300">
        {/* Card sparkles effect */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <SparklesComponent 
            particleColor={agent.status === "completed" ? "#22c55e" : agent.status === "running" ? "#3b82f6" : "#f472b6"} 
            particleDensity={20}
            minSize={1}
            maxSize={3}
          />
        </div>
        
        <CardHeader className="pb-3 relative z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <motion.div
                className={`p-3 rounded-xl ${
                  agent.status === "completed"
                    ? "bg-green-400/20 border border-green-400/30"
                    : agent.status === "running"
                    ? "bg-blue-400/20 border border-blue-400/30"
                    : agent.status === "error"
                    ? "bg-red-400/20 border border-red-400/30"
                    : "bg-gray-400/20 border border-gray-400/30"
                }`}
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Icon
                  className={`h-6 w-6 ${
                    agent.status === "completed"
                      ? "text-green-400"
                      : agent.status === "running"
                      ? "text-blue-400"
                      : agent.status === "error"
                      ? "text-red-400"
                      : "text-gray-400"
                  }`}
                />
              </motion.div>
              <div>
                <CardTitle className="text-lg text-white">
                  {formatAgentName(agent.agent_name)}
                </CardTitle>
                <CardDescription className="text-sm text-gray-300">
                  {description}
                </CardDescription>
              </div>
            </div>
            <Badge 
              className={`ml-auto ${
                agent.status === "completed"
                  ? "bg-green-400/20 text-green-300 border-green-400/30"
                  : agent.status === "running"
                  ? "bg-blue-400/20 text-blue-300 border-blue-400/30"
                  : agent.status === "error"
                  ? "bg-red-400/20 text-red-300 border-red-400/30"
                  : "bg-gray-400/20 text-gray-300 border-gray-400/30"
              }`}
            >
              <StatusIcon
                className={`h-3 w-3 mr-1 ${
                  agent.status === "running" ? "animate-spin" : ""
                }`}
              />
              {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 relative z-10">
          <div className="relative">
            <Progress
              value={agent.progress_percentage}
              className="h-3"
            />
            <motion.div
              className={`absolute inset-0 rounded-full opacity-30 ${
                agent.status === "completed"
                  ? "bg-gradient-to-r from-green-400/20 to-emerald-400/20"
                  : agent.status === "running"
                  ? "bg-gradient-to-r from-blue-400/20 to-cyan-400/20"
                  : "bg-gradient-to-r from-pink-400/20 to-amber-400/20"
              }`}
              animate={{ opacity: [0.2, 0.4, 0.2] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-300">{agent.message}</span>
            <span className="font-bold text-white text-base">{agent.progress_percentage}%</span>
          </div>
          {agent.ai_generated && (
            <motion.div 
              className="flex items-center text-xs text-pink-300 bg-pink-400/10 rounded-lg px-3 py-2 border border-pink-400/20"
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              <Sparkles className="mr-2 h-3 w-3" />
              AI-powered generation
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
