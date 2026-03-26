import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CampaignEditor from "../components/CampaignEditor";
import { getCampaign } from "../services/api";
import type { Campaign } from "../types";

const CampaignEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getCampaign(id)
      .then(setCampaign)
      .catch(() => setError("Failed to load campaign"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleCampaignSaved = () => {
    navigate("/");
  };

  const handleCancel = () => {
    navigate("/");
  };

  if (loading) return <div className="loading-state">Loading campaign...</div>;
  if (error || !campaign)
    return <div className="error-message">{error ?? "Campaign not found"}</div>;

  return (
    <CampaignEditor
      campaign={campaign}
      onCampaignSaved={handleCampaignSaved}
      onCancel={handleCancel}
    />
  );
};

export default CampaignEditPage;
