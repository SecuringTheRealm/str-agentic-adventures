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
          <div className={styles.emptyImageState}>
            <p>No image available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageDisplay;
