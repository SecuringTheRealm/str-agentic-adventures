import type React from "react";
import { useNavigate } from "react-router-dom";
import CampaignSelection from "../components/CampaignSelection";
import type { Campaign } from "../types";

const CampaignSelectionPage: React.FC = () => {
  const navigate = useNavigate();

  const handleCampaignCreated = (campaign: Campaign) => {
    navigate(`/campaigns/${campaign.id}/characters`);
  };

  return <CampaignSelection onCampaignCreated={handleCampaignCreated} />;
};

export default CampaignSelectionPage;
