import type React from "react";
import styles from "./ImageDisplay.module.css";

interface ImageDisplayProps {
  imageUrl: string | null;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ imageUrl }) => {
  return (
    <div className={styles.imageDisplay}>
      <div className={styles.imageContainer}>
        {imageUrl ? (
          <img src={imageUrl} alt="Game Visualization" />
        ) : (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>🏰</div>
            <p>Scene will appear as the story unfolds</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageDisplay;
