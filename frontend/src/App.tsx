import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LandingPage } from "@/pages/LandingPage";
import { CampaignCreate } from "@/pages/CampaignCreate";
import { CampaignDashboard } from "@/pages/CampaignDashboard";
import { CampaignResults } from "@/pages/CampaignResults";

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/create" element={<CampaignCreate />} />
            <Route path="/campaign/:id" element={<CampaignDashboard />} />
            <Route path="/campaign/:id/results" element={<CampaignResults />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
