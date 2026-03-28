import { Mic } from "lucide-react";
import type React from "react";
import styles from "./VoiceMicButton.module.css";

interface VoiceMicButtonProps {
  isListening: boolean;
  disabled: boolean;
  onPressStart: () => void;
  onPressEnd: () => void;
}

const VoiceMicButton: React.FC<VoiceMicButtonProps> = ({
  isListening,
  disabled,
  onPressStart,
  onPressEnd,
}) => (
  <button
    type="button"
    className={`${styles.micButton} ${isListening ? styles.active : ""}`}
    onMouseDown={onPressStart}
    onMouseUp={onPressEnd}
    onMouseLeave={onPressEnd}
    onTouchStart={onPressStart}
    onTouchEnd={onPressEnd}
    disabled={disabled}
    data-listening={isListening}
    aria-label={
      isListening ? "Recording — release to send" : "Hold to speak (microphone)"
    }
  >
    <Mic size={18} />
  </button>
);

export default VoiceMicButton;
