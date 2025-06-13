import React from 'react';
import './PredefinedCharacters.css';
import { predefinedCharacters } from '../data/predefinedCharacters';
import type { Character } from '../services/api';

interface PredefinedCharactersProps {
  onCharacterSelected: (character: Character) => void;
  onBack: () => void;
}

const PredefinedCharacters: React.FC<PredefinedCharactersProps> = ({
  onCharacterSelected,
  onBack
}) => {
  const handleCharacterSelect = (characterTemplate: Omit<Character, 'id'>) => {
    // Create a character with a unique ID
    const character: Character = {
      ...characterTemplate,
      id: `predefined-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    onCharacterSelected(character);
  };

  const getAbilityModifier = (score: number): string => {
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : modifier.toString();
  };

  return (
    <div className="predefined-characters">
      <div className="predefined-characters-header">
        <h2>Choose a Pre-Defined Character</h2>
        <p>Select from these balanced, ready-to-play characters</p>
        <button onClick={onBack} className="back-button">
          ← Back to Character Options
        </button>
      </div>

      <div className="characters-grid">
        {predefinedCharacters.map((character, index) => (
          <div key={index} className="character-card">
            <div className="character-header">
              <h3>{character.name}</h3>
              <div className="character-basics">
                Level {character.level} {character.race} {character.character_class}
              </div>
            </div>

            <div className="character-stats">
              <div className="hit-points">
                <span className="stat-label">Hit Points</span>
                <span className="stat-value">
                  {character.hit_points.current}/{character.hit_points.maximum}
                </span>
              </div>

              <div className="abilities-grid">
                <div className="ability">
                  <span className="ability-name">STR</span>
                  <span className="ability-score">{character.abilities.strength}</span>
                  <span className="ability-modifier">{getAbilityModifier(character.abilities.strength)}</span>
                </div>
                <div className="ability">
                  <span className="ability-name">DEX</span>
                  <span className="ability-score">{character.abilities.dexterity}</span>
                  <span className="ability-modifier">{getAbilityModifier(character.abilities.dexterity)}</span>
                </div>
                <div className="ability">
                  <span className="ability-name">CON</span>
                  <span className="ability-score">{character.abilities.constitution}</span>
                  <span className="ability-modifier">{getAbilityModifier(character.abilities.constitution)}</span>
                </div>
                <div className="ability">
                  <span className="ability-name">INT</span>
                  <span className="ability-score">{character.abilities.intelligence}</span>
                  <span className="ability-modifier">{getAbilityModifier(character.abilities.intelligence)}</span>
                </div>
                <div className="ability">
                  <span className="ability-name">WIS</span>
                  <span className="ability-score">{character.abilities.wisdom}</span>
                  <span className="ability-modifier">{getAbilityModifier(character.abilities.wisdom)}</span>
                </div>
                <div className="ability">
                  <span className="ability-name">CHA</span>
                  <span className="ability-score">{character.abilities.charisma}</span>
                  <span className="ability-modifier">{getAbilityModifier(character.abilities.charisma)}</span>
                </div>
              </div>

              <div className="equipment-preview">
                <h4>Equipment</h4>
                <ul>
                  {character.inventory.slice(0, 4).map((item, itemIndex) => (
                    <li key={itemIndex}>
                      {item.name}
                      {item.quantity > 1 && ` (${item.quantity})`}
                    </li>
                  ))}
                  {character.inventory.length > 4 && (
                    <li>...and {character.inventory.length - 4} more items</li>
                  )}
                </ul>
              </div>
            </div>

            <button 
              onClick={() => handleCharacterSelect(character)}
              className="select-character-button"
            >
              Select This Character
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PredefinedCharacters;