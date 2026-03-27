import type React from "react";
import { Badge } from "@/components/ui/badge";
import styles from "./CompactStatusBar.module.css";

interface CompactStatusBarProps {
  currentHp: number;
  maxHp: number;
  armorClass: number;
  level: number;
  conditions?: string[];
}

function getHpColorClass(current: number, max: number): string {
  if (max <= 0) return styles.hpBarGreen;
  const ratio = current / max;
  if (ratio > 0.5) return styles.hpBarGreen;
  if (ratio > 0.25) return styles.hpBarYellow;
  return styles.hpBarRed;
}

const CompactStatusBar: React.FC<CompactStatusBarProps> = ({
  currentHp,
  maxHp,
  armorClass,
  level,
  conditions = [],
}) => {
  const hpPercent = maxHp > 0 ? Math.max(0, (currentHp / maxHp) * 100) : 0;
  const hpColorClass = getHpColorClass(currentHp, maxHp);

  return (
    <div className={styles.statusBar} data-testid="compact-status-bar">
      <div className={styles.hpSection}>
        <span className={styles.hpLabel}>HP</span>
        <div
          className={styles.hpBarTrack}
          role="progressbar"
          aria-valuenow={currentHp}
          aria-valuemin={0}
          aria-valuemax={maxHp}
          aria-label={`Hit points: ${currentHp} of ${maxHp}`}
        >
          <div
            className={`${styles.hpBarFill} ${hpColorClass}`}
            style={{ width: `${hpPercent}%` }}
          />
        </div>
        <span className={styles.hpText}>
          {currentHp}/{maxHp}
        </span>
      </div>

      <div className={styles.divider} />

      <div className={styles.statItem}>
        <span className={styles.statItemLabel}>AC</span>
        <span className={styles.statItemValue} data-testid="ac-value">
          {armorClass}
        </span>
      </div>

      <div className={styles.divider} />

      <div className={styles.statItem}>
        <span className={styles.statItemLabel}>Lv</span>
        <span className={styles.statItemValue}>{level}</span>
      </div>

      {conditions.length > 0 && (
        <div className={styles.conditions}>
          {conditions.map((condition) => (
            <Badge key={condition} variant="secondary">
              {condition}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

export default CompactStatusBar;
