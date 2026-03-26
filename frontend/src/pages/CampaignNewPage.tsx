import React from "react";
import { useNavigate } from "react-router-dom";
import type { Campaign } from "../types";
import CampaignEditor from "../components/CampaignEditor";

const CampaignNewPage: React.FC = () => {
  const navigate = useNavigate();

  const handleCampaignSaved = (campaign: Campaign) => {
    navigate(`/campaigns/${campaign.id}/characters`);
  };

  const handleCancel = () => {
    navigate("/");
  };

  return (
    <CampaignEditor onCampaignSaved={handleCampaignSaved} onCancel={handleCancel} />
  );
};

export default CampaignNewPage;
