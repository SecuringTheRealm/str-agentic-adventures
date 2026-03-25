import { useId, useState } from "react";
import "./App.css";
import CampaignSelection from "./components/CampaignSelection";
import CharacterSelection from "./components/CharacterSelection";
import GameInterface from "./components/GameInterface";
import type { Campaign, Character } from "./services/api";

function App() {
  const mainId = useId();
  const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
  const [currentCharacter, setCurrentCharacter] = useState<Character | null>(
    null
  );
  const [gameStarted, setGameStarted] = useState(false);
  const [showCharacterSelection, setShowCharacterSelection] = useState(false);

  const handleCampaignCreated = (campaign: Campaign) => {
    setCurrentCampaign(campaign);
    setShowCharacterSelection(true);
  };

  const handleCharacterSelected = (character: Character) => {
    setCurrentCharacter(character);
    setShowCharacterSelection(false);
    setGameStarted(true);
  };

  const handleBackToCampaigns = () => {
    setCurrentCampaign(null);
    setCurrentCharacter(null);
    setGameStarted(false);
    setShowCharacterSelection(false);
  };

  return (
    <div className="App">
      <a href={`#${mainId}`} className="skip-link">
        Skip to main content
      </a>
      <header className="App-header">
        <h1>Securing the Realm - Agentic Adventures</h1>
        {gameStarted && (
          <button
            type="button"
            onClick={handleBackToCampaigns}
            className="back-button"
          >
            ← Back to Campaigns
          </button>
        )}
      </header>

      <main id={mainId} className="App-main">
        {!gameStarted && !showCharacterSelection ? (
          <div className="campaign-setup">
            <CampaignSelection onCampaignCreated={handleCampaignCreated} />
          </div>
        ) : showCharacterSelection && currentCampaign ? (
          <div className="character-setup">
            <CharacterSelection
              campaign={currentCampaign}
              onCharacterSelected={handleCharacterSelected}
              onBackToCampaigns={handleBackToCampaigns}
            />
          </div>
        ) : (
          currentCampaign &&
          currentCharacter && (
            <GameInterface
              campaign={currentCampaign}
              character={currentCharacter}
            />
          )
        )}
      </main>
    </div>
  );
}

export default App;
