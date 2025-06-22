import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  TrendingUp,
  Edit3,
  Image,
  Calendar,
  ArrowRight,
  Sparkles,
  BarChart3,
  Zap,
  Globe,
  CheckCircle,
  Rocket,
  ChevronDown,
} from "lucide-react";

export function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: TrendingUp,
      title: "Trend Analyzer",
      description: "Discovers viral trends using Google Trends API",
      color: "from-blue-500 to-cyan-500",
      delay: 0,
    },
    {
      icon: Edit3,
      title: "Content Writer",
      description: "Creates engaging content with Google Gemini AI",
      color: "from-purple-500 to-pink-500",
      delay: 0.1,
    },
    {
      icon: Image,
      title: "Visual Designer",
      description: "Curates professional images via Unsplash",
      color: "from-pink-500 to-rose-500",
      delay: 0.2,
    },
    {
      icon: Calendar,
      title: "Campaign Scheduler",
      description: "Optimizes timing for maximum engagement",
      color: "from-green-500 to-emerald-500",
      delay: 0.3,
    },
  ];

  const steps = [
    {
      icon: Zap,
      title: "Input Your Campaign Goals",
      description: "Tell us about your business and campaign objectives",
    },
    {
      icon: BarChart3,
      title: "AI Agents Analyze & Create",
      description:
        "Our 4 specialized agents work together to build your campaign",
    },
    {
      icon: Globe,
      title: "Get Comprehensive Results",
      description: "Receive platform-specific content, visuals, and scheduling",
    },
  ];

  return (
    <div className="min-h-screen overflow-hidden">
      {/* Animated background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-purple-100 via-pink-50 to-blue-100">
        <div className="absolute inset-0 bg-gradient-to-t from-white/50 to-transparent" />
      </div>

      {/* Floating shapes animation */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 bg-purple-400/10 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ top: "10%", left: "10%" }}
        />
        <motion.div
          className="absolute w-96 h-96 bg-blue-400/10 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ bottom: "10%", right: "10%" }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center">
          <div className="container mx-auto px-4 py-20">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center max-w-5xl mx-auto"
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-200 mb-8"
              >
                <Sparkles className="w-5 h-5 text-purple-600" />
                <span className="text-sm font-medium text-purple-700">
                  Powered by 4 Specialized AI Agents
                </span>
              </motion.div>

              <motion.h1
                className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                  Generate Viral
                </span>
                <br />
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Campaigns with AI
                </span>
              </motion.h1>

              <motion.p
                className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                VyralFlow AI uses cutting-edge artificial intelligence to create
                data-driven social media campaigns that capture attention and
                drive engagement.
              </motion.p>

              <motion.div
                className="flex flex-col sm:flex-row gap-4 justify-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                <Button
                  size="lg"
                  onClick={() => navigate("/create")}
                  className="group relative px-8 py-6 text-lg font-semibold overflow-hidden"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 group-hover:from-purple-700 group-hover:to-pink-700 transition-all duration-300" />
                  <span className="relative flex items-center gap-2 text-white">
                    Create Your Viral Campaign
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Button>
              </motion.div>

              {/* Animated arrow */}
              <motion.div
                className="mt-20"
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <ChevronDown className="w-8 h-8 text-gray-400 mx-auto" />
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-32 relative">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-5xl md:text-6xl font-bold mb-6">
                <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  4 AI Agents
                </span>{" "}
                Working for You
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Each specialized agent brings unique capabilities to create
                comprehensive campaigns
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: feature.delay }}
                  viewport={{ once: true }}
                  className="group"
                >
                  <Card className="h-full border-0 shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden hover:-translate-y-2">
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                    />
                    <CardContent className="relative pt-8 pb-6">
                      <motion.div
                        className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${feature.color} mb-6`}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <feature.icon className="w-8 h-8 text-white" />
                      </motion.div>
                      <h3 className="text-2xl font-bold mb-3">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600 leading-relaxed">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="py-32 bg-gradient-to-b from-gray-50 to-white">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-5xl md:text-6xl font-bold mb-6">
                How{" "}
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  VyralFlow AI
                </span>{" "}
                Works
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Simple, powerful, and designed for results
              </p>
            </motion.div>

            <div className="max-w-5xl mx-auto">
              {steps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className="flex items-center gap-8 mb-12"
                >
                  <motion.div
                    className="relative"
                    whileHover={{ scale: 1.1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-xl opacity-30" />
                    <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 w-24 h-24 rounded-full flex items-center justify-center">
                      <step.icon className="w-12 h-12 text-white" />
                    </div>
                  </motion.div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">
                      <span className="text-purple-600">0{index + 1}.</span>
                      {step.title}
                    </h3>
                    <p className="text-gray-600 text-lg">{step.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-32 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-600 via-pink-600 to-blue-600" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />

          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 0.1 }}
            transition={{ duration: 1 }}
            viewport={{ once: true }}
          >
            <div className="absolute inset-0 bg-grid-white/10 bg-[size:50px_50px]" />
          </motion.div>

          <div className="container mx-auto px-4 text-center relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                transition={{ duration: 0.5 }}
                viewport={{ once: true }}
                className="inline-flex p-4 rounded-full bg-white/10 backdrop-blur mb-8"
              >
                <Rocket className="w-12 h-12 text-white" />
              </motion.div>

              <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
                Ready to Go Viral?
              </h2>
              <p className="text-xl md:text-2xl text-white/90 mb-10 max-w-3xl mx-auto">
                Join thousands of businesses using VyralFlow AI to create
                campaigns that capture attention and drive results.
              </p>

              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  size="lg"
                  onClick={() => navigate("/create")}
                  className="px-10 py-6 text-lg font-semibold bg-white text-purple-600 hover:bg-gray-100 shadow-2xl"
                >
                  <span className="flex items-center gap-2">
                    Start Creating Now
                    <ArrowRight className="w-5 h-5" />
                  </span>
                </Button>
              </motion.div>

              {/* Success badges */}
              <motion.div
                className="mt-12 flex flex-wrap justify-center gap-4"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                viewport={{ once: true }}
              >
                {[
                  "5-minute setup",
                  "No credit card required",
                  "100% AI-powered",
                ].map((text, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur rounded-full"
                  >
                    <CheckCircle className="w-4 h-4 text-white" />
                    <span className="text-sm text-white font-medium">
                      {text}
                    </span>
                  </div>
                ))}
              </motion.div>
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  );
}
