import React from 'react';
import './ImageDisplay.css';

interface ImageDisplayProps {
  imageUrl: string | null;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ imageUrl }) => {
  return (
    <div className="image-display">
      <div className="image-container">
        {imageUrl ? (
          <img src={imageUrl} alt="Game Visualization" />
        ) : (
          <div className="empty-image-state">
            <p>No image available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageDisplay;
