import React from "react";
import EnterpriseHeader from "../components/homepage/EnterpriseHeader";
import HeroSection from "../components/homepage/HeroSection";
import TrustBar from "../components/homepage/TrustBar";
import ProblemSection from "../components/homepage/ProblemSection";
import SolutionSection from "../components/homepage/SolutionSection";
import HowItWorksSection from "../components/homepage/HowItWorksSection";
import PlatformCapabilities from "../components/homepage/PlatformCapabilities";
import SecurityGovernance from "../components/homepage/SecurityGovernance";
import WhoForSection from "../components/homepage/WhoForSection";
import PlaygroundCTA from "../components/homepage/PlaygroundCTA";
import FinalCTA from "../components/homepage/FinalCTA";
import EnterpriseFooter from "../components/homepage/EnterpriseFooter";

const Home: React.FC = () => (
  <>
    <EnterpriseHeader />
    <HeroSection />
    <TrustBar />
    <ProblemSection />
    <SolutionSection />
    <HowItWorksSection />
    <PlatformCapabilities />
    <SecurityGovernance />
    <WhoForSection />
    <PlaygroundCTA />
    <FinalCTA />
    <EnterpriseFooter />
  </>
);

export default Home;
