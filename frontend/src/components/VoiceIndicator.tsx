import type React from "react";
import styles from "./VoiceIndicator.module.css";

interface VoiceIndicatorProps {
  isSpeaking: boolean;
}

const VoiceIndicator: React.FC<VoiceIndicatorProps> = ({ isSpeaking }) => {
  if (!isSpeaking) return null;
  return (
    <div
      className={styles.indicator}
      role="status"
      aria-label="Dungeon Master is speaking"
    >
      <div className={styles.dot} />
      <span className={styles.label}>DM is speaking...</span>
      <div className={styles.waveform}>
        {(["b0", "b1", "b2", "b3", "b4"] as const).map((id, i) => (
          <div
            key={id}
            className={styles.bar}
            style={{ animationDelay: `${i * 0.1}s` }}
          />
        ))}
      </div>
    </div>
  );
};

export default VoiceIndicator;
