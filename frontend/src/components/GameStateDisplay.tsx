import type React from "react";
import { useEffect, useState } from "react";
import styles from "./GameStateDisplay.module.css";

interface GameSession {
  session_id: string;
  campaign_id: string;
  type: string;
  status: string;
  current_scene: string;
  available_actions: string[];
  scene_count: number;
  started_at: string;
}

interface CombatState {
  combat_id: string;
  status: string;
  round: number;
  current_turn: number;
  initiative_order: Array<{
    type: string;
    id: string;
    name: string;
    initiative: number;
  }>;
  environment: string;
}

interface GameStateDisplayProps {
  session?: GameSession | null;
  combatState?: CombatState | null;
  websocket?: WebSocket | null;
  onActionSelect?: (action: string) => void;
  onCombatAction?: (action: string, data: any) => void;
}

const GameStateDisplay: React.FC<GameStateDisplayProps> = ({
  session,
  combatState,
  websocket,
  onActionSelect,
  onCombatAction,
}) => {
  const [selectedAction, setSelectedAction] = useState<string>("");
  const [actionDescription, setActionDescription] = useState<string>("");
  const [targetId, setTargetId] = useState<string>("");

  // Reset action selection when session changes
  useEffect(() => {
    setSelectedAction("");
    setActionDescription("");
    setTargetId("");
  }, []);

  const handleActionSubmit = () => {
    if (!selectedAction.trim()) return;

    if (combatState && combatState.status === "active") {
      // Combat action
      if (onCombatAction) {
        onCombatAction(selectedAction, {
          description: actionDescription,
          target_id: targetId,
          combat_id: combatState.combat_id,
        });
      }
    } else {
      // Regular session action
      if (onActionSelect) {
        onActionSelect(selectedAction);
      }
    }

    // Reset form
    setSelectedAction("");
    setActionDescription("");
    setTargetId("");
  };

  const getCurrentTurnCharacter = () => {
    if (!combatState || !combatState.initiative_order.length) return null;
    return combatState.initiative_order[combatState.current_turn];
  };

  const getNextTurnCharacter = () => {
    if (!combatState || !combatState.initiative_order.length) return null;
    const nextTurn =
      (combatState.current_turn + 1) % combatState.initiative_order.length;
    return combatState.initiative_order[nextTurn];
  };

  return (
    <div className={styles.gameStateDisplay}>
      {/* Session Information */}
      {session && (
        <div className={styles.sessionInfo}>
          <div className={styles.sessionHeader}>
            <h3>Game Session</h3>
            <div className={styles.sessionStatus}>
              <span className={`status-indicator ${session.status}`}>
                {session.status.toUpperCase()}
              </span>
              <span className={styles.sessionType}>{session.type}</span>
            </div>
          </div>

          <div className={styles.currentScene}>
            <h4>Current Scene:</h4>
            <p>{session.current_scene}</p>
            <div className={styles.sceneMeta}>
              <span>Scene {session.scene_count}</span>
              <span>
                Started: {new Date(session.started_at).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Combat State */}
      {combatState && combatState.status === "active" && (
        <div className={styles.combatState}>
          <div className={styles.combatHeader}>
            <h3>Combat</h3>
            <div className={styles.combatInfo}>
              <span className={styles.round}>Round {combatState.round}</span>
              <span className={styles.environment}>
                {combatState.environment}
              </span>
            </div>
          </div>

          <div className={styles.initiativeTracker}>
            <h4>Initiative Order:</h4>
            <div className={styles.initiativeList}>
              {combatState.initiative_order.map((participant, index) => (
                <div
                  key={participant.id}
                  className={`initiative-item ${
                    index === combatState.current_turn ? "current-turn" : ""
                  } ${participant.type}`}
                >
                  <div className={styles.participantInfo}>
                    <span className={styles.name}>{participant.name}</span>
                    <span className={styles.type}>{participant.type}</span>
                  </div>
                  <div className={styles.initiativeScore}>
                    {participant.initiative}
                  </div>
                  {index === combatState.current_turn && (
                    <div className={styles.turnIndicator}>▶</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className={styles.currentTurnInfo}>
            {(() => {
              const currentChar = getCurrentTurnCharacter();
              const nextChar = getNextTurnCharacter();
              return (
                <div>
                  <div className={styles.currentTurn}>
                    <strong>Current Turn: </strong>
                    {currentChar
                      ? `${currentChar.name} (${currentChar.type})`
                      : "Unknown"}
                  </div>
                  <div className={styles.nextTurn}>
                    <strong>Next Up: </strong>
                    {nextChar
                      ? `${nextChar.name} (${nextChar.type})`
                      : "Round End"}
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* Available Actions */}
      {session?.available_actions && session.available_actions.length > 0 && (
        <div className={styles.availableActions}>
          <h4>Available Actions:</h4>
          <div className={styles.actionSelection}>
            <select
              value={selectedAction}
              onChange={(e) => setSelectedAction(e.target.value)}
              className={styles.actionSelect}
            >
              <option value="">Select an action...</option>
              {session.available_actions.map((action, index) => (
                <option key={index} value={action}>
                  {action}
                </option>
              ))}
            </select>

            {selectedAction && (
              <div className={styles.actionDetails}>
                <textarea
                  value={actionDescription}
                  onChange={(e) => setActionDescription(e.target.value)}
                  placeholder="Describe your action in detail..."
                  className={styles.actionDescription}
                  rows={3}
                />

                {combatState &&
                  (selectedAction.toLowerCase().includes("attack") ||
                    selectedAction.toLowerCase().includes("target")) && (
                    <select
                      value={targetId}
                      onChange={(e) => setTargetId(e.target.value)}
                      className={styles.targetSelect}
                    >
                      <option value="">Select target...</option>
                      {combatState.initiative_order
                        .filter((p) => p.type === "npc")
                        .map((target) => (
                          <option key={target.id} value={target.id}>
                            {target.name}
                          </option>
                        ))}
                    </select>
                  )}

                <button
                  onClick={handleActionSubmit}
                  className={styles.submitActionButton}
                  disabled={!selectedAction.trim()}
                >
                  {combatState ? "Take Combat Action" : "Take Action"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick Combat Actions */}
      {combatState && combatState.status === "active" && (
        <div className={styles.quickActions}>
          <h4>Quick Combat Actions:</h4>
          <div className={styles.quickActionButtons}>
            <button
              onClick={() => {
                setSelectedAction("Attack");
                setActionDescription("Make a melee attack");
              }}
              className="quick-action-button attack"
            >
              ⚔️ Attack
            </button>
            <button
              onClick={() => {
                setSelectedAction("Cast a spell");
                setActionDescription("Cast a spell");
              }}
              className="quick-action-button spell"
            >
              ✨ Spell
            </button>
            <button
              onClick={() => {
                setSelectedAction("Move");
                setActionDescription("Move to a new position");
              }}
              className="quick-action-button move"
            >
              🏃 Move
            </button>
            <button
              onClick={() => {
                setSelectedAction("Defend");
                setActionDescription("Take a defensive stance");
              }}
              className="quick-action-button defend"
            >
              🛡️ Defend
            </button>
            <button
              onClick={() => {
                setSelectedAction("Use an item");
                setActionDescription("Use an item from inventory");
              }}
              className="quick-action-button item"
            >
              🎒 Item
            </button>
          </div>
        </div>
      )}

      {/* Connection Status */}
      {websocket && (
        <div className={styles.connectionStatus}>
          <div
            className={`connection-indicator ${
              websocket.readyState === WebSocket.OPEN
                ? "connected"
                : "disconnected"
            }`}
          >
            {websocket.readyState === WebSocket.OPEN
              ? "🟢 Connected"
              : "🔴 Disconnected"}
          </div>
        </div>
      )}
    </div>
  );
};

export default GameStateDisplay;
