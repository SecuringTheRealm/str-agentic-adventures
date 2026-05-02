import type React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Campaign, Character } from "../types";
import CharacterCreation from "./CharacterCreation";
import styles from "./CharacterSelection.module.css";
import PredefinedCharacters from "./PredefinedCharacters";

interface CharacterSelectionProps {
  campaign: Campaign;
  onCharacterSelected: (character: Character) => void;
  onBackToCampaigns: () => void;
}

const CharacterSelection: React.FC<CharacterSelectionProps> = ({
  campaign,
  onCharacterSelected,
  onBackToCampaigns,
}) => {
  const [selectionMode, setSelectionMode] = useState<
    "choose" | "create" | "predefined"
  >("choose");

  const handleBackToChoice = () => {
    setSelectionMode("choose");
  };

  if (selectionMode === "create") {
    return (
      <CharacterCreation
        campaign={campaign}
        onCharacterCreated={onCharacterSelected}
        onBack={handleBackToChoice}
      />
    );
  }

  if (selectionMode === "predefined") {
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
        <p>
          Campaign: <strong>{campaign.name}</strong>
        </p>
        <Button
          type="button"
          variant="ghost"
          onClick={onBackToCampaigns}
          className={styles.backButton}
        >
          ← Back to Campaigns
        </Button>
      </div>

      <div className={styles.characterOptions}>
        <Card className={styles.characterOptionCard}>
          <CardHeader>
            <div className={styles.cardIcon}>⚔️</div>
            <CardTitle className={styles.cardTitle}>
              Create New Character
            </CardTitle>
            <CardDescription className={styles.cardDescription}>
              Build your own custom character with full D&D 5e customisation
              options.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className={styles.featureList}>
              <li>Choose from multiple races and classes</li>
              <li>Customise ability scores</li>
              <li>Add personal backstory</li>
              <li>Full control over your character's build</li>
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              type="button"
              onClick={() => setSelectionMode("create")}
              className={styles.characterOptionButton}
              data-testid="create-character-btn"
            >
              Create Character
            </Button>
          </CardFooter>
        </Card>

        <Card className={styles.characterOptionCard}>
          <CardHeader>
            <div className={styles.cardIcon}>📜</div>
            <CardTitle className={styles.cardTitle}>
              Choose Pre-Defined Character
            </CardTitle>
            <CardDescription className={styles.cardDescription}>
              Select from a curated list of ready-to-play characters for quick
              starts.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className={styles.featureList}>
              <li>Balanced character builds</li>
              <li>Complete equipment sets</li>
              <li>Perfect for new players</li>
              <li>Jump straight into the adventure</li>
            </ul>
          </CardContent>
          <CardFooter>
            <Button
              type="button"
              onClick={() => setSelectionMode("predefined")}
              className={styles.characterOptionButton}
              data-testid="browse-characters-btn"
            >
              Browse Characters
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default CharacterSelection;
