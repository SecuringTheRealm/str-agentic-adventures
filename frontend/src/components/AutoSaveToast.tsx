import type React from "react";
import { useEffect, useState } from "react";
import styles from "./AutoSaveToast.module.css";

interface AutoSaveToastProps {
  /** Timestamp string from state_updates.last_auto_save; changes trigger the toast */
  lastAutoSave: string | null;
}

const TOAST_DURATION_MS = 2500;

const AutoSaveToast: React.FC<AutoSaveToastProps> = ({ lastAutoSave }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!lastAutoSave) return;

    setVisible(true);
    const timer = setTimeout(() => setVisible(false), TOAST_DURATION_MS);
    return () => clearTimeout(timer);
  }, [lastAutoSave]);

  if (!visible) return null;

  return (
    <div className={styles.toast} role="status" aria-live="polite">
      ✓ Auto-saved
    </div>
  );
};

export default AutoSaveToast;
