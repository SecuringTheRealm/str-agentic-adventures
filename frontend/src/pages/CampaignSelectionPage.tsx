import React from "react";
import { useNavigate } from "react-router-dom";
import type { Campaign } from "../types";
import CampaignSelection from "../components/CampaignSelection";

const CampaignSelectionPage: React.FC = () => {
  const navigate = useNavigate();

  const handleCampaignCreated = (campaign: Campaign) => {
    navigate(`/campaigns/${campaign.id}/characters`);
  };

  return <CampaignSelection onCampaignCreated={handleCampaignCreated} />;
};

export default CampaignSelectionPage;
