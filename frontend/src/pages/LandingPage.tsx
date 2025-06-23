import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { GradientBackground } from "@/components/ui/gradient-bg";
import { FloatingParticles } from "@/components/ui/floating-particles";
import { FloatingShapes } from "@/components/ui/floating-shapes";
import { Sparkles as SparklesComponent } from "@/components/ui/sparkles";
import { BeamContainer } from "@/components/ui/beam";
import { AnimatedGridPattern } from "@/components/ui/grid-pattern";
import { Meteors } from "@/components/ui/meteors";
import {
  TrendingUp,
  Edit3,
  Image,
  Calendar,
  ArrowRight,
  Sparkles,
  CheckCircle,
  Rocket,
  Stars,
  Brain,
  Target,
  Wand2,
} from "lucide-react";

export function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: TrendingUp,
      title: "Trend Analyzer",
      description: "AI-powered trend discovery using real-time data analysis to identify viral opportunities",
      color: "from-pink-500 to-rose-500",
      delay: 0,
    },
    {
      icon: Edit3,
      title: "Content Writer",
      description: "Generate compelling, platform-specific content with advanced language models",
      color: "from-rose-500 to-pink-500",
      delay: 0.1,
    },
    {
      icon: Image,
      title: "Visual Designer",
      description: "Create stunning visuals with intelligent image curation and design principles",
      color: "from-amber-500 to-yellow-500",
      delay: 0.2,
    },
    {
      icon: Calendar,
      title: "Campaign Scheduler",
      description: "Optimize timing for maximum engagement and reach across all platforms",
      color: "from-yellow-500 to-amber-500",
      delay: 0.3,
    },
  ];

  const steps = [
    {
      icon: Target,
      title: "Define Your Vision",
      description:
        "Tell our AI about your brand, goals, and target audience for personalized campaign generation that resonates with your market.",
      gradient: "from-pink-500 to-rose-500",
    },
    {
      icon: Brain,
      title: "AI Analysis & Creation",
      description:
        "Our specialized agents analyze trends, create content, design visuals, and plan optimal timing using advanced machine learning.",
      gradient: "from-rose-500 to-pink-500",
    },
    {
      icon: Rocket,
      title: "Launch & Dominate",
      description:
        "Get ready-to-use campaigns with platform-specific content designed to go viral and drive maximum engagement.",
      gradient: "from-amber-500 to-yellow-500",
    },
  ];


  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
      {/* Background */}
      <GradientBackground />
      <FloatingParticles />
      <FloatingShapes />

      {/* Navigation */}
      <nav className="relative z-50 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <img 
                src="/vyralflow.png" 
                alt="VyralFlow AI Logo" 
                className="w-10 h-10 object-contain"
              />
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                VyralFlow AI
              </span>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-6"
            >
              <Button
                variant="ghost"
                className="text-gray-300 hover:text-white hover:bg-white/10"
                onClick={() => navigate("/create")}
              >
                Create Campaign
              </Button>
              <Button
                className="bg-gradient-to-r from-pink-500 to-amber-500 text-white border-0 hover:from-pink-600 hover:to-amber-600"
                onClick={() => navigate("/create")}
              >
                Get Started
              </Button>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center pt-20">
          {/* Enhanced Background Effects */}
          <SparklesComponent 
            className="opacity-60" 
            particleColor="#f472b6" 
            particleDensity={80}
          />
          <Meteors number={15} />
          <AnimatedGridPattern 
            width={60} 
            height={60} 
            className="opacity-20"
            maxOpacity={0.3}
          />
          
          <div className="container mx-auto px-6 py-20 relative z-10">
            <BeamContainer>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center max-w-6xl mx-auto"
              >
              {/* Badge */}
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-black/40 backdrop-blur-lg border border-pink-500/30 mb-8 hover:bg-black/60 transition-all duration-300"
              >
                <Stars className="w-5 h-5 text-pink-400" />
                <span className="text-sm font-medium text-white">
                  Powered by 4 Specialized AI Agents
                </span>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              </motion.div>

              {/* Main Heading */}
              <motion.h1
                className="text-6xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <span className="block text-white mb-2">
                  Create Viral
                </span>
                <span className="block bg-gradient-to-r from-pink-400 via-rose-400 to-amber-400 bg-clip-text text-transparent">
                  AI Campaigns
                </span>
                <span className="block text-2xl md:text-3xl lg:text-4xl mt-6 text-gray-300 font-normal">
                  that capture attention & drive results
                </span>
              </motion.h1>

              {/* Description */}
              <motion.p
                className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                Transform your social media presence with AI-powered campaigns
                that understand trends, create compelling content, and optimize
                for maximum viral potential.
              </motion.p>

              {/* CTA Button */}
              <motion.div
                className="flex justify-center mb-16"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative group"
                >
                  <div className="absolute -inset-1 bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-glow" />
                  <Button
                    size="lg"
                    onClick={() => navigate("/create")}
                    className="relative px-12 py-6 text-xl font-semibold bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 text-white border-0 rounded-full hover:shadow-2xl transition-all duration-300"
                  >
                    <span className="flex items-center gap-3">
                      <Wand2 className="w-6 h-6" />
                      Create Viral Campaign Now
                      <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                    </span>
                  </Button>
                </motion.div>
              </motion.div>


              {/* Trust Indicators */}
              <motion.div
                className="flex flex-wrap justify-center gap-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 1.0 }}
              >
                {[
                  "AI-Powered",
                  "Real-time Trends",
                  "Multi-Platform",
                  "Instant Results",
                ].map((text, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 1.0 + index * 0.1 }}
                    className="flex items-center gap-2 px-4 py-2 bg-black/20 backdrop-blur-lg rounded-full border border-gray-600/30 hover:border-pink-400/30 transition-all duration-300"
                  >
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-gray-300 font-medium">
                      {text}
                    </span>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>
            </BeamContainer>
          </div>

          {/* Scroll Indicator */}
          <motion.div
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center">
              <motion.div
                className="w-1 h-3 bg-pink-400 rounded-full mt-2"
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="py-32 relative">
          {/* Section Background Effects */}
          <div className="absolute inset-0 overflow-hidden">
            <AnimatedGridPattern 
              width={80} 
              height={80} 
              className="opacity-10"
              maxOpacity={0.2}
            />
          </div>
          
          <div className="container mx-auto px-6 relative z-10">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-20"
            >
              <motion.div
                initial={{ scale: 0.9 }}
                whileInView={{ scale: 1 }}
                transition={{ duration: 0.5 }}
                viewport={{ once: true }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black/20 backdrop-blur-lg border border-pink-500/30 mb-8"
              >
                <Sparkles className="w-5 h-5 text-pink-400" />
                <span className="text-sm font-medium text-white">
                  AI Agent Ecosystem
                </span>
              </motion.div>

              <h2 className="text-5xl md:text-6xl font-bold mb-6 text-white">
                Four Specialized AI Agents
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Each agent brings unique capabilities to create comprehensive,
                data-driven campaigns that dominate social media
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
                  <Card className="h-full bg-black/20 backdrop-blur-lg border border-gray-600/30 hover:border-pink-400/40 transition-all duration-500 overflow-hidden hover:bg-black/30 group relative">
                    {/* Card sparkles effect */}
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                      <SparklesComponent 
                        particleColor="#f472b6" 
                        particleDensity={30}
                        minSize={2}
                        maxSize={4}
                      />
                    </div>
                    
                    <CardContent className="p-8 text-center relative z-10">
                      <motion.div
                        className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${feature.color} mb-6 relative`}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <feature.icon className="w-8 h-8 text-white relative z-10" />
                        <div
                          className={`absolute inset-0 bg-gradient-to-r ${feature.color} rounded-2xl blur opacity-50`}
                        />
                      </motion.div>
                      <h3 className="text-2xl font-bold mb-4 text-white">
                        {feature.title}
                      </h3>
                      <p className="text-gray-300 leading-relaxed">
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
        <section className="py-32 relative">
          <div className="container mx-auto px-6">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold mb-6 text-white">
                How It Works
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Three simple steps to viral success with AI-powered intelligence
              </p>
            </motion.div>

            <div className="max-w-6xl mx-auto space-y-20">
              {steps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className={`flex items-center gap-12 ${
                    index % 2 === 1 ? "flex-row-reverse" : ""
                  }`}
                >
                  <motion.div
                    className="relative flex-shrink-0"
                    whileHover={{ scale: 1.1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <div
                      className={`absolute inset-0 bg-gradient-to-r ${step.gradient} rounded-full blur-xl opacity-50`}
                    />
                    <div
                      className={`relative bg-gradient-to-r ${step.gradient} w-24 h-24 rounded-full flex items-center justify-center border border-pink-200/20`}
                    >
                      <step.icon className="w-12 h-12 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-black/50 backdrop-blur-lg rounded-full flex items-center justify-center border border-pink-200/30">
                      <span className="text-sm font-bold text-white">
                        {index + 1}
                      </span>
                    </div>
                  </motion.div>
                  <div className="flex-1">
                    <h3 className="text-3xl font-bold mb-4 text-white">
                      {step.title}
                    </h3>
                    <p className="text-gray-300 text-lg leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="py-32 relative">
          <div className="absolute inset-0 bg-gradient-to-r from-pink-900/20 via-rose-900/20 to-amber-900/20 backdrop-blur-3xl" />

          <div className="container mx-auto px-6 text-center relative z-10">
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
                className="inline-flex p-6 rounded-full bg-gradient-to-r from-pink-500/20 to-amber-500/20 backdrop-blur-lg border border-pink-200/20 mb-8"
              >
                <img 
                  src="/vyralflow.png" 
                  alt="VyralFlow AI Logo" 
                  className="w-16 h-16 object-contain"
                />
              </motion.div>

              <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
                Ready to Go Viral?
              </h2>
              <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto">
                Join thousands of creators and businesses using VyralFlow AI to
                dominate social media with intelligent, data-driven campaigns.
              </p>

              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative group inline-block"
              >
                <div className="absolute -inset-1 bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
                <Button
                  size="lg"
                  onClick={() => navigate("/create")}
                  className="relative px-12 py-6 text-xl font-semibold bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 text-white border-0 rounded-full"
                >
                  <span className="flex items-center gap-3">
                    Start Creating Now
                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  );
}