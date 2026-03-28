import type React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { Campaign, Character, DiceResult } from "../types";
import BattleMap from "./BattleMap";
import CharacterSheet from "./CharacterSheet";
import ChatBox from "./ChatBox";
import CompactStatusBar from "./CompactStatusBar";
import DiceRoller from "./DiceRoller";
import ImageDisplay from "./ImageDisplay";
import MobileDrawer from "./MobileDrawer";
import styles from "./MobileGameLayout.module.css";

type TabId = "chat" | "character" | "gamestate" | "map";

interface MobileGameLayoutProps {
  character: Character;
  campaign: Campaign;
  messages: Array<{ text: string; sender: "player" | "dm" }>;
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  streamingMessage?: string;
  suggestedActions?: string[];
  onSuggestedAction?: (action: string) => void;
  currentImage: string | null;
  battleMapUrl: string | null;
  combatActive: boolean;
  imageLoading: boolean;
  imagesRemaining: number | null;
  imageGenerationAvailable: boolean;
  imageGenerationStatusMessage: string | null;
  onGeneratePortrait: () => void;
  onGenerateScene: () => void;
  onGenerateBattleMap: () => void;
  diceRollerProps: {
    characterId?: string;
    playerName?: string;
    websocket?: WebSocket | null;
    webSocketDiceResult?: DiceResult | null;
    onRoll?: (result: DiceResult) => void;
  };
}

const tabs: Array<{ id: TabId; label: string }> = [
  { id: "chat", label: "Chat" },
  { id: "character", label: "Character" },
  { id: "gamestate", label: "Visuals" },
  { id: "map", label: "Map" },
];

const MobileGameLayout: React.FC<MobileGameLayoutProps> = ({
  character,
  messages,
  onSendMessage,
  isLoading,
  streamingMessage,
  suggestedActions,
  onSuggestedAction,
  currentImage,
  battleMapUrl,
  combatActive,
  imageLoading,
  imagesRemaining,
  imageGenerationAvailable,
  imageGenerationStatusMessage,
  onGeneratePortrait,
  onGenerateScene,
  onGenerateBattleMap,
  diceRollerProps,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>("chat");
  const [diceDrawerOpen, setDiceDrawerOpen] = useState(false);
  const hitPoints = character.hit_points ?? character.hitPoints;
  const visualsDisabled =
    imageLoading || imagesRemaining === 0 || !imageGenerationAvailable;
  const disabledReason =
    imageGenerationStatusMessage ||
    (imagesRemaining === 0 ? "Image limit reached for this session." : null);

  const renderVisualButton = (
    label: string,
    onClick: () => void,
    testId: string
  ) => {
    const button = (
      <Button
        variant="default"
        onClick={onClick}
        disabled={visualsDisabled}
        style={{ minHeight: 44 }}
        data-testid={testId}
      >
        {imageLoading ? "Generating..." : label}
      </Button>
    );

    if (!disabledReason || !visualsDisabled) {
      return button;
    }

    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={styles.visualButtonWrapper} tabIndex={0}>
            {button}
          </span>
        </TooltipTrigger>
        <TooltipContent>{disabledReason}</TooltipContent>
      </Tooltip>
    );
  };

  return (
    <div className={styles.mobileLayout} data-testid="mobile-game-layout">
      <CompactStatusBar
        currentHp={hitPoints?.current ?? 0}
        maxHp={hitPoints?.maximum ?? 0}
        armorClass={10}
        level={character.level ?? 1}
      />

      <div className={styles.tabBar} role="tablist" aria-label="Game sections">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant="ghost"
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            className={`${styles.tabButton} ${activeTab === tab.id ? styles.tabButtonActive : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      <div className={styles.tabContent}>
        {activeTab === "chat" && (
          <div id="panel-chat" role="tabpanel" className={styles.tabPanel}>
            <ChatBox
              messages={messages}
              onSendMessage={onSendMessage}
              isLoading={isLoading}
              streamingMessage={streamingMessage}
              suggestedActions={suggestedActions}
              onSuggestedAction={onSuggestedAction}
            />
          </div>
        )}

        {activeTab === "character" && (
          <div id="panel-character" role="tabpanel" className={styles.tabPanel}>
            <CharacterSheet character={character} />
          </div>
        )}

        {activeTab === "gamestate" && (
          <div id="panel-gamestate" role="tabpanel" className={styles.tabPanel}>
            <TooltipProvider delayDuration={150}>
              <div className={styles.visualsPanel}>
                <h4>Generate Visuals</h4>
                {imageGenerationStatusMessage && (
                  <div
                    className={styles.visualStatus}
                    role="status"
                    data-testid="visual-generation-status"
                  >
                    {imageGenerationStatusMessage}
                  </div>
                )}
                {imagesRemaining !== null && (
                  <p className={styles.imageBudget}>
                    {imagesRemaining > 0
                      ? `${imagesRemaining} illustration${imagesRemaining === 1 ? "" : "s"} remaining`
                      : "Image limit reached"}
                  </p>
                )}
                {renderVisualButton(
                  "Character Portrait",
                  onGeneratePortrait,
                  "generate-portrait-button"
                )}
                {renderVisualButton(
                  "Scene Illustration",
                  onGenerateScene,
                  "generate-scene-button"
                )}
                {renderVisualButton(
                  "Battle Map",
                  onGenerateBattleMap,
                  "generate-battle-map-button"
                )}
                <ImageDisplay imageUrl={currentImage} />
              </div>
            </TooltipProvider>
          </div>
        )}

        {activeTab === "map" && (
          <div id="panel-map" role="tabpanel" className={styles.tabPanel}>
            {combatActive ? (
              <BattleMap mapUrl={battleMapUrl} />
            ) : (
              <div
                style={{
                  padding: 16,
                  color: "var(--color-text-muted-warm)",
                  fontFamily: "Cinzel, serif",
                }}
              >
                No active battle map. Start combat to see the tactical map.
              </div>
            )}
          </div>
        )}
      </div>

      <button
        type="button"
        className={styles.fab}
        onClick={() => setDiceDrawerOpen(true)}
        aria-label="Open dice roller"
        data-testid="dice-fab"
      >
        <span aria-hidden="true" role="img">
          🎲
        </span>
      </button>

      <MobileDrawer
        open={diceDrawerOpen}
        onClose={() => setDiceDrawerOpen(false)}
        title="Dice Roller"
        side="right"
      >
        <DiceRoller
          characterId={diceRollerProps.characterId}
          playerName={diceRollerProps.playerName}
          websocket={diceRollerProps.websocket}
          webSocketDiceResult={diceRollerProps.webSocketDiceResult}
          onRoll={diceRollerProps.onRoll}
        />
      </MobileDrawer>
    </div>
  );
};

export default MobileGameLayout;
