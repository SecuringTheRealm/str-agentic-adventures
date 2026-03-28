import type React from "react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import GameInterface from "../components/GameInterface";
import { getCampaign, getCharacter } from "../services/api";
import type { Campaign, Character } from "../types";

const GamePage: React.FC = () => {
  const { id, characterId } = useParams<{ id: string; characterId: string }>();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || !characterId) return;
    setLoading(true);
    Promise.all([getCampaign(id), getCharacter(characterId)])
      .then(([campaignData, characterData]) => {
        setCampaign(campaignData);
        setCharacter(characterData);
      })
      .catch(() => setError("Failed to load game data"))
      .finally(() => setLoading(false));
  }, [id, characterId]);

  if (loading) return <div className="loading-state">Loading game...</div>;
  if (error || !campaign || !character)
    return (
      <div className="error-message">{error ?? "Game data not found"}</div>
    );

  return <GameInterface campaign={campaign} character={character} />;
};

export default GamePage;
