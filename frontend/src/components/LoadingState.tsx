import type React from "react";
import styles from "./LoadingState.module.css";

interface LoadingStateProps {
  message?: string;
}

const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading...",
}) => (
  <div className={styles.container} role="status" aria-live="polite">
    <div className={styles.spinner} aria-hidden="true" />
    <p className={styles.message}>{message}</p>
  </div>
);

export default LoadingState;
