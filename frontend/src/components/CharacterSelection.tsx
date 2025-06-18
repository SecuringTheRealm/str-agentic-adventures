import React, { useState } from 'react';
import styles from "./CharacterSelection.module.css";
import CharacterCreation from './CharacterCreation';
import PredefinedCharacters from './PredefinedCharacters';
import type { Character, Campaign } from '../services/api';

interface CharacterSelectionProps {
  campaign: Campaign;
  onCharacterSelected: (character: Character) => void;
  onBackToCampaigns: () => void;
}

const CharacterSelection: React.FC<CharacterSelectionProps> = ({
  campaign,
  onCharacterSelected,
  onBackToCampaigns
}) => {
  const [selectionMode, setSelectionMode] = useState<'choose' | 'create' | 'predefined'>('choose');

  const handleBackToChoice = () => {
    setSelectionMode('choose');
  };

  if (selectionMode === 'create') {
    return (
      <CharacterCreation
        campaign={campaign}
        onCharacterCreated={onCharacterSelected}
        onBack={handleBackToChoice}
      />
    );
  }

  if (selectionMode === 'predefined') {
    return (
      <PredefinedCharacters
        onCharacterSelected={onCharacterSelected}
        onBack={handleBackToChoice}
      />
    );
  }

  return (
    <div className={styles.characterSelection}>
      <div className={styles.characterSelectionHeader}>
        <h2>Choose Your Character</h2>
        <p>Campaign: <strong>{campaign.name}</strong></p>
        <button 
          onClick={onBackToCampaigns} 
          className={`${styles.backButton} ${styles.secondary}`}
        >
          ← Back to Campaigns
        </button>
      </div>

      <div className={styles.characterOptions}>
        <div className={styles.characterOption}>
          <div className={styles.characterOptionCard}>
            <h3>Create New Character</h3>
            <p>Build your own custom character with full D&D 5e customization options.</p>
            <ul>
              <li>Choose from multiple races and classes</li>
              <li>Customize ability scores</li>
              <li>Add personal backstory</li>
              <li>Full control over your character's build</li>
            </ul>
            <button 
              onClick={() => setSelectionMode('create')}
              className={`${styles.characterOptionButton} ${styles.primary}`}
            >
              Create Character
            </button>
          </div>
        </div>

        <div className={styles.characterOption}>
          <div className={styles.characterOptionCard}>
            <h3>Choose Pre-Defined Character</h3>
            <p>Select from a curated list of ready-to-play characters for quick starts.</p>
            <ul>
              <li>Balanced character builds</li>
              <li>Complete equipment sets</li>
              <li>Perfect for new players</li>
              <li>Jump straight into the adventure</li>
            </ul>
            <button 
              onClick={() => setSelectionMode('predefined')}
              className={`${styles.characterOptionButton} ${styles.primary}`}
            >
              Browse Characters
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CharacterSelection;