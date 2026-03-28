import type React from "react";
import { Button } from "@/components/ui/button";
import styles from "./FloorRequestCard.module.css";

interface FloorRequestCardProps {
  visible: boolean;
  onGrantFloor: () => void;
}

const FloorRequestCard: React.FC<FloorRequestCardProps> = ({
  visible,
  onGrantFloor,
}) => {
  if (!visible) return null;
  return (
    <div
      className={styles.card}
      role="alert"
      aria-label="Dungeon Master wants to speak"
    >
      <div className={styles.icon}>✋</div>
      <div className={styles.text}>DM has something to say</div>
      <Button size="sm" variant="secondary" onClick={onGrantFloor}>
        Let them speak
      </Button>
    </div>
  );
};

export default FloorRequestCard;
