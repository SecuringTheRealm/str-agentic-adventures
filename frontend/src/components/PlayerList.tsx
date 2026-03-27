import type { SessionParticipant } from "@/types";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import styles from "./PlayerList.module.css";

export interface PlayerListProps {
  /** List of session participants to display. */
  participants: SessionParticipant[];
  /** The character_id whose turn it currently is (if any). */
  currentTurnCharacterId?: string | null;
}

/**
 * Displays the list of connected (and disconnected) players in a multiplayer
 * game session.  Highlights whose turn it is with a badge and bold text.
 */
const PlayerList: React.FC<PlayerListProps> = ({
  participants,
  currentTurnCharacterId,
}) => {
  return (
    <Card className={styles.container}>
      <CardHeader>
        <CardTitle className={styles.title}>Players</CardTitle>
      </CardHeader>
      <CardContent>
        {participants.length === 0 ? (
          <p className={styles.emptyState}>No players have joined yet.</p>
        ) : (
          <div className={styles.list}>
            {participants.map((p) => {
              const isTurn = currentTurnCharacterId === p.character_id;
              return (
                <div key={p.id} className={styles.playerRow}>
                  <span
                    className={`${styles.statusDot} ${
                      p.is_connected ? styles.connected : styles.disconnected
                    }`}
                    data-testid={`status-${p.id}`}
                  />
                  <span
                    className={`${styles.playerName} ${
                      isTurn ? styles.currentTurn : ""
                    }`}
                  >
                    {p.player_name}
                  </span>
                  {p.is_dm && <Badge variant="secondary">DM</Badge>}
                  {isTurn && <Badge>Turn</Badge>}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PlayerList;
