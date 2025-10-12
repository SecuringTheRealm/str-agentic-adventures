import type React from "react";
import { predefinedCharacters } from "../data/predefinedCharacters";
import type { Character } from "../services/api";
import styles from "./PredefinedCharacters.module.css";

interface PredefinedCharactersProps {
  onCharacterSelected: (character: Character) => void;
  onBack: () => void;
}

const PredefinedCharacters: React.FC<PredefinedCharactersProps> = ({
  onCharacterSelected,
  onBack,
}) => {
  const handleCharacterSelect = (characterTemplate: Omit<Character, "id">) => {
    // Create a character with a unique ID
    const character: Character = {
      ...characterTemplate,
      id: `predefined-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
    onCharacterSelected(character);
  };

  const getAbilityModifier = (score: number): string => {
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : modifier.toString();
  };

  return (
    <div className={styles.predefinedCharacters}>
      <div className={styles.predefinedCharactersHeader}>
        <h2>Choose a Pre-Defined Character</h2>
        <p>Select from these balanced, ready-to-play characters</p>
        <button type="button" onClick={onBack} className={styles.backButton}>
          ← Back to Character Options
        </button>
      </div>

      <div className={styles.charactersGrid}>
        {predefinedCharacters.map((character) => (
          <div
            key={character.id || character.name}
            className={styles.characterCard}
          >
            <div className={styles.characterHeader}>
              <h3>{character.name}</h3>
              <div className={styles.characterBasics}>
                Level {character.level} {character.race}{" "}
                {character.character_class}
              </div>
            </div>

            <div className={styles.characterStats}>
              <div className={styles.hitPoints}>
                <span className={styles.statLabel}>Hit Points</span>
                <span className={styles.statValue}>
                  {character.hit_points.current}/{character.hit_points.maximum}
                </span>
              </div>

              <div className={styles.abilitiesGrid}>
                <div className={styles.ability}>
                  <span className={styles.abilityName}>STR</span>
                  <span className={styles.abilityScore}>
                    {character.abilities.strength || 10}
                  </span>
                  <span className={styles.abilityModifier}>
                    {getAbilityModifier(character.abilities.strength || 10)}
                  </span>
                </div>
                <div className={styles.ability}>
                  <span className={styles.abilityName}>DEX</span>
                  <span className={styles.abilityScore}>
                    {character.abilities.dexterity || 10}
                  </span>
                  <span className={styles.abilityModifier}>
                    {getAbilityModifier(character.abilities.dexterity || 10)}
                  </span>
                </div>
                <div className={styles.ability}>
                  <span className={styles.abilityName}>CON</span>
                  <span className={styles.abilityScore}>
                    {character.abilities.constitution || 10}
                  </span>
                  <span className={styles.abilityModifier}>
                    {getAbilityModifier(character.abilities.constitution || 10)}
                  </span>
                </div>
                <div className={styles.ability}>
                  <span className={styles.abilityName}>INT</span>
                  <span className={styles.abilityScore}>
                    {character.abilities.intelligence || 10}
                  </span>
                  <span className={styles.abilityModifier}>
                    {getAbilityModifier(character.abilities.intelligence || 10)}
                  </span>
                </div>
                <div className={styles.ability}>
                  <span className={styles.abilityName}>WIS</span>
                  <span className={styles.abilityScore}>
                    {character.abilities.wisdom || 10}
                  </span>
                  <span className={styles.abilityModifier}>
                    {getAbilityModifier(character.abilities.wisdom || 10)}
                  </span>
                </div>
                <div className={styles.ability}>
                  <span className={styles.abilityName}>CHA</span>
                  <span className={styles.abilityScore}>
                    {character.abilities.charisma || 10}
                  </span>
                  <span className={styles.abilityModifier}>
                    {getAbilityModifier(character.abilities.charisma || 10)}
                  </span>
                </div>
              </div>

              <div className={styles.equipmentPreview}>
                <h4>Equipment</h4>
                <ul>
                  {(character.inventory || []).slice(0, 4).map((item) => (
                    <li key={item.item_id || (item as any).name}>
                      {(item as any).name || item.item_id}
                      {item.quantity > 1 && ` (${item.quantity})`}
                    </li>
                  ))}
                  {(character.inventory || []).length > 4 && (
                    <li>
                      ...and {(character.inventory || []).length - 4} more items
                    </li>
                  )}
                </ul>
              </div>
            </div>

            <button
              type="button"
              onClick={() => handleCharacterSelect(character)}
              className={styles.selectCharacterButton}
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
