import type React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import styles from "./ErrorState.module.css";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  showBackLink?: boolean;
}

const ErrorState: React.FC<ErrorStateProps> = ({
  message,
  onRetry,
  showBackLink = true,
}) => {
  const navigate = useNavigate();

  return (
    <div className={styles.container} role="alert">
      <div className={styles.icon} aria-hidden="true">
        &#x1F6E1;&#xFE0F;
      </div>
      <h2 className={styles.heading}>Quest Interrupted</h2>
      <p className={styles.message}>{message}</p>
      <p className={styles.hint}>
        The path ahead is unclear. Try retracing your steps.
      </p>
      <div className={styles.actions}>
        {onRetry ? (
          <Button className={styles.retryButton} onClick={onRetry}>
            Try Again
          </Button>
        ) : (
          <Button
            className={styles.retryButton}
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        )}
        {showBackLink && (
          <Button
            variant="outline"
            className={styles.backButton}
            onClick={() => navigate("/")}
          >
            Back to Campaigns
          </Button>
        )}
      </div>
    </div>
  );
};

export default ErrorState;
