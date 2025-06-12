import React, { useState } from 'react';
import './App.css';
import CampaignCreation from './components/CampaignCreation';
import GameInterface from './components/GameInterface';
import type { Campaign, Character } from './services/api';

function App() {
  const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
  const [currentCharacter, setCurrentCharacter] = useState<Character | null>(null);
  const [gameStarted, setGameStarted] = useState(false);

  const handleCampaignCreated = (campaign: Campaign) => {
    setCurrentCampaign(campaign);
    // For demo purposes, create a sample character
    // In a real app, this would come from character creation
    const sampleCharacter: Character = {
      id: "demo-char-1",
      name: "Adventurer",
      race: "Human",
      character_class: "Fighter",
      level: 1,
      abilities: {
        strength: 16,
        dexterity: 14,
        constitution: 15,
        intelligence: 12,
        wisdom: 13,
        charisma: 10
      },
      hit_points: {
        current: 12,
        maximum: 12
      },
      inventory: []
    };
    setCurrentCharacter(sampleCharacter);
    setGameStarted(true);
  };

  const handleBackToCampaigns = () => {
    setCurrentCampaign(null);
    setCurrentCharacter(null);
    setGameStarted(false);
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
        {!gameStarted ? (
          <div className="campaign-setup">
            <CampaignCreation onCampaignCreated={handleCampaignCreated} />
          </div>
        ) : (
          currentCampaign && currentCharacter && (
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
