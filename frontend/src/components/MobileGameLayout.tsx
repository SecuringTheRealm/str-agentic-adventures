import type React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import type { Character, DiceResult } from "../types";
import type { Campaign } from "../types";
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
  onGeneratePortrait,
  onGenerateScene,
  onGenerateBattleMap,
  diceRollerProps,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>("chat");
  const [diceDrawerOpen, setDiceDrawerOpen] = useState(false);

  return (
    <div className={styles.mobileLayout} data-testid="mobile-game-layout">
      <CompactStatusBar
        currentHp={character.hit_points.current}
        maxHp={character.hit_points.maximum}
        armorClass={10}
        level={character.level}
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
          <div
            id="panel-chat"
            role="tabpanel"
            className={styles.tabPanel}
          >
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
          <div
            id="panel-character"
            role="tabpanel"
            className={styles.tabPanel}
          >
            <CharacterSheet character={character} />
          </div>
        )}

        {activeTab === "gamestate" && (
          <div
            id="panel-gamestate"
            role="tabpanel"
            className={styles.tabPanel}
          >
            <div className={styles.visualsPanel}>
              <h4>Generate Visuals</h4>
              {imagesRemaining !== null && (
                <p style={{ fontSize: "0.75rem", color: "var(--color-gold-stone)", margin: 0 }}>
                  {imagesRemaining > 0
                    ? `${imagesRemaining} illustration${imagesRemaining === 1 ? "" : "s"} remaining`
                    : "Image limit reached"}
                </p>
              )}
              <Button
                variant="default"
                onClick={onGeneratePortrait}
                disabled={imageLoading || imagesRemaining === 0}
                style={{ minHeight: 44 }}
              >
                {imageLoading ? "Generating..." : "Character Portrait"}
              </Button>
              <Button
                variant="default"
                onClick={onGenerateScene}
                disabled={imageLoading || imagesRemaining === 0}
                style={{ minHeight: 44 }}
              >
                {imageLoading ? "Generating..." : "Scene Illustration"}
              </Button>
              <Button
                variant="default"
                onClick={onGenerateBattleMap}
                disabled={imageLoading || imagesRemaining === 0}
                style={{ minHeight: 44 }}
              >
                {imageLoading ? "Generating..." : "Battle Map"}
              </Button>
              <ImageDisplay imageUrl={currentImage} />
            </div>
          </div>
        )}

        {activeTab === "map" && (
          <div
            id="panel-map"
            role="tabpanel"
            className={styles.tabPanel}
          >
            {combatActive ? (
              <BattleMap mapUrl={battleMapUrl} />
            ) : (
              <div style={{ padding: 16, color: "var(--color-text-muted-warm)", fontFamily: "Cinzel, serif" }}>
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
