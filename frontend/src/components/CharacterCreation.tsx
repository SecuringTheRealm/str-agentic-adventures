import React, { useState } from "react";
import styles from "./CharacterCreation.module.css";
import type {
  Character,
  CharacterCreateRequest,
  Campaign,
} from "../services/api";
import { createCharacter } from "../services/api";

interface CharacterCreationProps {
  campaign: Campaign;
  onCharacterCreated: (character: Character) => void;
  onBack: () => void;
}

const CharacterCreation: React.FC<CharacterCreationProps> = ({
  campaign,
  onCharacterCreated,
  onBack,
}) => {
  const [formData, setFormData] = useState<CharacterCreateRequest>({
    name: "",
    race: "human",
    character_class: "fighter",
    abilities: {
      strength: 13,
      dexterity: 13,
      constitution: 13,
      intelligence: 13,
      wisdom: 13,
      charisma: 13,
    },
    backstory: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const races = [
    "Human",
    "Elf",
    "Dwarf",
    "Halfling",
    "Dragonborn",
    "Gnome",
    "Half-Elf",
    "Half-Orc",
    "Tiefling",
  ];

  const classes = [
    "Barbarian",
    "Bard",
    "Cleric",
    "Druid",
    "Fighter",
    "Monk",
    "Paladin",
    "Ranger",
    "Rogue",
    "Sorcerer",
    "Warlock",
    "Wizard",
  ];

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;

    if (name.startsWith("abilities.")) {
      const abilityName = name.split(".")[1] as keyof typeof formData.abilities;
      setFormData((prev) => ({
        ...prev,
        abilities: {
          ...prev.abilities,
          [abilityName]: parseInt(value) || 8,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const getTotalPoints = () => {
    return Object.values(formData.abilities).reduce(
      (sum, value) => sum + value,
      0
    );
  };

  const getAbilityModifier = (score: number): string => {
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : modifier.toString();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError("Character name is required");
      return;
    }

    const totalPoints = getTotalPoints();
    if (totalPoints !== 78) {
      // Standard array equivalent: 15+14+13+12+10+8 = 72, plus 6 for racial bonuses
      setError(
        `Ability scores must total 78 points (currently ${totalPoints})`
      );
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const character = await createCharacter(formData);
      onCharacterCreated(character);
    } catch (err: any) {
      // Extract error message from API response
      let errorMessage = "Failed to create character. Please try again.";

      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          // Validation errors from FastAPI
          errorMessage = err.response.data.detail
            .map((e: any) => e.msg)
            .join(", ");
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      console.error("Character creation error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.characterCreation}>
      <div className={styles.characterCreationHeader}>
        <h2>Create Your Character</h2>
        <p>
          Campaign: <strong>{campaign.name}</strong>
        </p>
        <button onClick={onBack} className={styles.backButton}>
          ← Back to Character Options
        </button>
      </div>

      <form onSubmit={handleSubmit} className={styles.characterForm}>
        <div className={styles.formSection}>
          <h3>Basic Information</h3>

          <div className={styles.formGroup}>
            <label htmlFor="name">Character Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Enter character name"
              required
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="race">Race</label>
              <select
                id="race"
                name="race"
                value={formData.race}
                onChange={handleInputChange}
              >
                {races.map((race) => (
                  <option key={race} value={race}>
                    {race}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="character_class">Class</label>
              <select
                id="character_class"
                name="character_class"
                value={formData.character_class}
                onChange={handleInputChange}
              >
                {classes.map((cls) => (
                  <option key={cls} value={cls}>
                    {cls}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className={styles.formSection}>
          <h3>Ability Scores</h3>
          <p className={styles.abilityPointsInfo}>
            Total Points: {getTotalPoints()}/78 (Standard point buy equivalent)
          </p>

          <div className={styles.abilitiesGrid}>
            {Object.entries(formData.abilities).map(([ability, value]) => (
              <div key={ability} className={styles.abilityInput}>
                <label htmlFor={`abilities.${ability}`}>
                  {ability.charAt(0).toUpperCase() + ability.slice(1)}
                </label>
                <input
                  type="number"
                  id={`abilities.${ability}`}
                  name={`abilities.${ability}`}
                  value={value}
                  onChange={handleInputChange}
                  min="8"
                  max="18"
                />
                <span className={styles.modifier}>
                  {getAbilityModifier(value)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.formSection}>
          <h3>Backstory (Optional)</h3>
          <div className={styles.formGroup}>
            <label htmlFor="backstory">Character Background</label>
            <textarea
              id="backstory"
              name="backstory"
              value={formData.backstory || ""}
              onChange={handleInputChange}
              placeholder="Tell us about your character's background, motivations, and history..."
              rows={4}
            />
          </div>
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <div className={styles.formActions}>
          <button
            type="submit"
            disabled={isSubmitting}
            className={styles.createButton}
          >
            {isSubmitting ? "Creating Character..." : "Create Character"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CharacterCreation;
