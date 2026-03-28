import type React from "react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CharacterSelection from "../components/CharacterSelection";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { getCampaign } from "../services/api";
import type { Campaign, Character } from "../types";

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

  if (loading) return <LoadingState message="Loading campaign..." />;
  if (error || !campaign)
    return <ErrorState message={error ?? "Campaign not found"} />;

  return (
    <CharacterSelection
      campaign={campaign}
      onCharacterSelected={handleCharacterSelected}
      onBackToCampaigns={handleBackToCampaigns}
    />
  );
};

export default CharacterSelectionPage;
