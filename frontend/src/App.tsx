import React, { useState } from 'react';
import './App.css';
import CampaignSelection from './components/CampaignSelection';
import CharacterCreation from './components/CharacterCreation';
import GameInterface from './components/GameInterface';
import type { Campaign, Character } from './services/api';

function App() {
  const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
  const [currentCharacter, setCurrentCharacter] = useState<Character | null>(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [showCharacterCreation, setShowCharacterCreation] = useState(false);

  const handleCampaignCreated = (campaign: Campaign) => {
    setCurrentCampaign(campaign);
    setShowCharacterCreation(true);
  };

  const handleCharacterCreated = (character: Character) => {
    setCurrentCharacter(character);
    setShowCharacterCreation(false);
    setGameStarted(true);
  };

  const handleBackToCampaigns = () => {
    setCurrentCampaign(null);
    setCurrentCharacter(null);
    setGameStarted(false);
    setShowCharacterCreation(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Securing the Realm - Agentic Adventures</h1>
        {gameStarted && (
          <button onClick={handleBackToCampaigns} className="back-button">
            ← Back to Campaigns
          </button>
        )}
      </header>
      
      <main className="App-main">
        {!currentCampaign ? (
          <div className="campaign-setup">
            <CampaignSelection onCampaignCreated={handleCampaignCreated} />
          </div>
        ) : showCharacterCreation ? (
          <div className="character-setup">
            <CharacterCreation 
              onCharacterCreated={handleCharacterCreated}
              onCancel={handleBackToCampaigns}
            />
          </div>
        ) : gameStarted && currentCharacter ? (
          <GameInterface 
            campaign={currentCampaign} 
            character={currentCharacter} 
          />
        ) : null}
      </main>
    </div>
  );
}

export default App;
