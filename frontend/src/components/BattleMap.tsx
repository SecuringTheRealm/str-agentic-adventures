import type React from "react";
import { useState } from "react";
import type { BattleMapData } from "@/types/battleMap";
import styles from "./BattleMap.module.css";
import TileGridRenderer from "./TileGridRenderer";

interface BattleMapProps {
  mapUrl: string | null;
  mapData?: BattleMapData | null;
  onTokenMove?: (tokenId: string, x: number, y: number) => void;
}

const BattleMap: React.FC<BattleMapProps> = ({
  mapUrl,
  mapData,
  onTokenMove,
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<"tile" | "image">("tile");

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  const hasBothViews = !!mapData && !!mapUrl;
  const showTileView = mapData && viewMode === "tile";
  const showImageView = mapUrl && (!mapData || viewMode === "image");

  return (
    <div className={`${styles.battleMap} ${expanded ? styles.expanded : ""}`}>
      <div className={styles.battleMapHeader}>
        <h3>Battle Map</h3>
        <div style={{ display: "flex", gap: "8px" }}>
          {hasBothViews && (
            <button
              type="button"
              onClick={() =>
                setViewMode(viewMode === "tile" ? "image" : "tile")
              }
              className={styles.toggleButton}
            >
              {viewMode === "tile" ? "Image View" : "Tile View"}
            </button>
          )}
          <button
            type="button"
            onClick={toggleExpand}
            className={styles.toggleButton}
          >
            {expanded ? "Minimize" : "Expand"}
          </button>
        </div>
      </div>

      <div className={styles.mapContainer}>
        {showTileView ? (
          <TileGridRenderer mapData={mapData} onTokenMove={onTokenMove} />
        ) : showImageView ? (
          <img src={mapUrl} alt="Tactical Battle Map" />
        ) : (
          <div className={styles.emptyMapState}>
            <p>No battle map available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BattleMap;
