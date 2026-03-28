import type React from "react";
import { useId, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type {
  Campaign,
  Character,
  CharacterCreateRequest,
} from "../services/api";
import { createCharacter } from "../services/api";
import styles from "./CharacterCreation.module.css";

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
  const nameId = useId();
  const raceId = useId();
  const classId = useId();
  const backstoryId = useId();

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
      setFormData((prev: CharacterCreateRequest) => ({
        ...prev,
        abilities: {
          ...prev.abilities,
          [abilityName]: Number.parseInt(value, 10) || 8,
        },
      }));
    } else {
      setFormData((prev: CharacterCreateRequest) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev: CharacterCreateRequest) => ({
      ...prev,
      [name]: value,
    }));
  };

  const getTotalPoints = () => {
    return Object.values(formData.abilities).reduce(
      (sum: number, value: number) => sum + value,
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
        <Button
          type="button"
          variant="ghost"
          onClick={onBack}
          className={styles.backButton}
        >
          ← Back to Character Options
        </Button>
      </div>

      <form onSubmit={handleSubmit} className={styles.characterForm}>
        <div className={styles.formSection}>
          <h3>Basic Information</h3>

          <div className={styles.formGroup}>
            <Label htmlFor={nameId}>Character Name</Label>
            <Input
              type="text"
              id={nameId}
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Enter character name"
              required
              data-testid="character-name-input"
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <Label htmlFor={raceId}>Race</Label>
              <Select
                value={formData.race}
                onValueChange={(value) => handleSelectChange("race", value)}
              >
                <SelectTrigger id={raceId} data-testid="character-race-select">
                  <SelectValue placeholder="Select a race" />
                </SelectTrigger>
                <SelectContent>
                  {races.map((race) => (
                    <SelectItem key={race} value={race.toLowerCase()}>
                      {race}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className={styles.formGroup}>
              <Label htmlFor={classId}>Class</Label>
              <Select
                value={formData.character_class}
                onValueChange={(value) =>
                  handleSelectChange("character_class", value)
                }
              >
                <SelectTrigger
                  id={classId}
                  data-testid="character-class-select"
                >
                  <SelectValue placeholder="Select a class" />
                </SelectTrigger>
                <SelectContent>
                  {classes.map((cls) => (
                    <SelectItem key={cls} value={cls.toLowerCase()}>
                      {cls}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className={styles.formSection}>
          <h3>Ability Scores</h3>
          <p className={styles.abilityPointsInfo}>
            Total Points: {getTotalPoints()}/78 (Standard point buy equivalent)
          </p>

          <div className={styles.abilitiesGrid}>
            {Object.entries(formData.abilities).map(
              ([ability, value]: [string, number]) => (
                <div key={ability} className={styles.abilityInput}>
                  <Label htmlFor={`abilities.${ability}`}>
                    {ability.charAt(0).toUpperCase() + ability.slice(1)}
                  </Label>
                  <Input
                    type="number"
                    id={`abilities.${ability}`}
                    name={`abilities.${ability}`}
                    value={value}
                    onChange={handleInputChange}
                    min={8}
                    max={18}
                    data-testid={`ability-${ability}`}
                  />
                  <span className={styles.modifier}>
                    {getAbilityModifier(value)}
                  </span>
                </div>
              )
            )}
          </div>
        </div>

        <div className={styles.formSection}>
          <h3>Backstory (Optional)</h3>
          <div className={styles.formGroup}>
            <Label htmlFor={backstoryId}>Character Background</Label>
            <Textarea
              id={backstoryId}
              name="backstory"
              value={formData.backstory || ""}
              onChange={handleInputChange}
              placeholder="Tell us about your character's background, motivations, and history..."
              rows={4}
              data-testid="character-backstory-input"
            />
          </div>
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <div className={styles.formActions}>
          <Button
            type="submit"
            disabled={isSubmitting}
            className={styles.createButton}
            data-testid="submit-character-btn"
          >
            {isSubmitting ? "Creating Character..." : "Create Character"}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CharacterCreation;
