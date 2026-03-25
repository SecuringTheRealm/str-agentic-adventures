import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CharacterSelection from "../components/CharacterSelection";
import { type Campaign, type Character, getCampaign } from "../services/api";

const CharacterSelectionPage: React.FC = () => {
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

  const handleCharacterSelected = (character: Character) => {
    navigate(`/campaigns/${id}/play/${character.id}`);
  };

  const handleBackToCampaigns = () => {
    navigate("/");
  };

  if (loading) return <div className="loading-state">Loading campaign...</div>;
  if (error || !campaign)
    return <div className="error-message">{error ?? "Campaign not found"}</div>;

  return (
    <CharacterSelection
      campaign={campaign}
      onCharacterSelected={handleCharacterSelected}
      onBackToCampaigns={handleBackToCampaigns}
    />
  );
};

export default CharacterSelectionPage;
