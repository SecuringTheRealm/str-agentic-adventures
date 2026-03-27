import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { getTileAsset, TILE_RENDER_SIZE } from "@/data/tileMapping";
import type { BattleMapData, MapToken, TeamType } from "@/types/battleMap";

interface TileGridRendererProps {
  mapData: BattleMapData;
  onTokenMove?: (tokenId: string, x: number, y: number) => void;
}

const TEAM_COLORS: Record<TeamType, string> = {
  player: "#22c55e",
  enemy: "#ef4444",
  neutral: "#3b82f6",
};

const TEAM_FILL_COLORS: Record<TeamType, string> = {
  player: "#166534",
  enemy: "#991b1b",
  neutral: "#1e3a5f",
};

/** Cache loaded tile images to avoid re-fetching. */
const imageCache = new Map<string, HTMLImageElement>();

function loadImage(src: string): Promise<HTMLImageElement> {
  const cached = imageCache.get(src);
  if (cached?.complete) return Promise.resolve(cached);

  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      imageCache.set(src, img);
      resolve(img);
    };
    img.onerror = reject;
    img.src = src;
  });
}

const TileGridRenderer: React.FC<TileGridRendererProps> = ({
  mapData,
  onTokenMove,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);
  const [scale, setScale] = useState(1);

  const tileSize = TILE_RENDER_SIZE;
  const mapPixelWidth = mapData.width * tileSize;
  const mapPixelHeight = mapData.height * tileSize;

  // Compute scale to fit container
  const updateScale = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    if (containerWidth === 0 || containerHeight === 0) return;

    const scaleX = containerWidth / mapPixelWidth;
    const scaleY = containerHeight / mapPixelHeight;
    setScale(Math.min(scaleX, scaleY, 1));
  }, [mapPixelWidth, mapPixelHeight]);

  useEffect(() => {
    updateScale();
    const handleResize = () => updateScale();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [updateScale]);

  // Main render function
  const renderCanvas = useCallback(async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = mapPixelWidth;
    canvas.height = mapPixelHeight;

    // Disable image smoothing for crisp pixel art
    ctx.imageSmoothingEnabled = false;

    // Clear
    ctx.fillStyle = "#1a1a2e";
    ctx.fillRect(0, 0, mapPixelWidth, mapPixelHeight);

    // Layer 1: Tiles
    const tilePromises: Promise<void>[] = [];
    for (let row = 0; row < mapData.height; row++) {
      for (let col = 0; col < mapData.width; col++) {
        const tile = mapData.tiles[row]?.[col];
        if (!tile) continue;
        const assetPath = getTileAsset(tile.type);
        const x = col * tileSize;
        const y = row * tileSize;
        tilePromises.push(
          loadImage(assetPath)
            .then((img) => {
              ctx.drawImage(img, x, y, tileSize, tileSize);
            })
            .catch(() => {
              // Fallback: draw a colored rect
              ctx.fillStyle = tile.passable ? "#4a4a5e" : "#2a2a3e";
              ctx.fillRect(x, y, tileSize, tileSize);
            }),
        );
      }
    }
    await Promise.all(tilePromises);

    // Layer 2: Entities
    const entityPromises: Promise<void>[] = [];
    for (const entity of mapData.entities) {
      const assetPath = getTileAsset(entity.type);
      const x = entity.x * tileSize;
      const y = entity.y * tileSize;
      entityPromises.push(
        loadImage(assetPath)
          .then((img) => {
            ctx.drawImage(img, x, y, tileSize, tileSize);
          })
          .catch(() => {
            ctx.fillStyle = "#8b5e3c";
            ctx.fillRect(x + 4, y + 4, tileSize - 8, tileSize - 8);
          }),
      );
    }
    await Promise.all(entityPromises);

    // Layer 3: Effects
    for (const effect of mapData.effects) {
      const colour = effect.colour ?? "rgba(255, 165, 0, 0.3)";
      const radius = effect.radius ?? 1;
      const centerX = effect.origin_x * tileSize + tileSize / 2;
      const centerY = effect.origin_y * tileSize + tileSize / 2;

      ctx.save();
      ctx.globalAlpha = 0.35;

      if (effect.type === "aoe_circle") {
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * tileSize, 0, Math.PI * 2);
        ctx.fillStyle = colour;
        ctx.fill();
      } else if (effect.type === "aoe_cone") {
        const dir = effect.direction ?? 0;
        const halfAngle = Math.PI / 4;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(
          centerX,
          centerY,
          radius * tileSize,
          dir - halfAngle,
          dir + halfAngle,
        );
        ctx.closePath();
        ctx.fillStyle = colour;
        ctx.fill();
      } else if (effect.type === "aoe_line") {
        const dir = effect.direction ?? 0;
        const lineWidth = tileSize * 0.5;
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(dir);
        ctx.fillStyle = colour;
        ctx.fillRect(0, -lineWidth / 2, radius * tileSize, lineWidth);
        ctx.restore();
      }

      // Draw label if present
      if (effect.label) {
        ctx.globalAlpha = 1;
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 12px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(effect.label, centerX, centerY - radius * tileSize - 4);
      }

      ctx.restore();
    }

    // Layer 4: Tokens
    for (const token of mapData.tokens) {
      const cx = token.x * tileSize + tileSize / 2;
      const cy = token.y * tileSize + tileSize / 2;
      const tokenRadius = tileSize * 0.38;
      const teamColor = TEAM_COLORS[token.team] ?? TEAM_COLORS.neutral;
      const fillColor = TEAM_FILL_COLORS[token.team] ?? TEAM_FILL_COLORS.neutral;

      // Selected highlight ring
      if (token.id === selectedTokenId) {
        ctx.beginPath();
        ctx.arc(cx, cy, tokenRadius + 5, 0, Math.PI * 2);
        ctx.strokeStyle = "#fbbf24";
        ctx.lineWidth = 3;
        ctx.stroke();
      }

      // Token circle
      ctx.beginPath();
      ctx.arc(cx, cy, tokenRadius, 0, Math.PI * 2);
      ctx.fillStyle = fillColor;
      ctx.fill();
      ctx.strokeStyle = teamColor;
      ctx.lineWidth = 2;
      ctx.stroke();

      // First letter of name
      ctx.fillStyle = "#ffffff";
      ctx.font = `bold ${Math.round(tileSize * 0.35)}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(token.name.charAt(0).toUpperCase(), cx, cy);

      // HP bar
      if (token.hp != null && token.max_hp != null && token.max_hp > 0) {
        const barWidth = tileSize * 0.7;
        const barHeight = 4;
        const barX = cx - barWidth / 2;
        const barY = cy - tokenRadius - 10;
        const hpRatio = Math.max(0, Math.min(1, token.hp / token.max_hp));

        // Background
        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(barX, barY, barWidth, barHeight);
        // HP fill
        ctx.fillStyle =
          hpRatio > 0.5 ? "#22c55e" : hpRatio > 0.25 ? "#eab308" : "#ef4444";
        ctx.fillRect(barX, barY, barWidth * hpRatio, barHeight);
        // Border
        ctx.strokeStyle = "#666";
        ctx.lineWidth = 1;
        ctx.strokeRect(barX, barY, barWidth, barHeight);
      }
    }

    // Layer 5: Grid overlay
    ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
    ctx.lineWidth = 1;
    for (let col = 0; col <= mapData.width; col++) {
      const x = col * tileSize;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, mapPixelHeight);
      ctx.stroke();
    }
    for (let row = 0; row <= mapData.height; row++) {
      const y = row * tileSize;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(mapPixelWidth, y);
      ctx.stroke();
    }
  }, [mapData, mapPixelWidth, mapPixelHeight, tileSize, selectedTokenId]);

  useEffect(() => {
    renderCanvas();
  }, [renderCanvas]);

  const handleCanvasClick = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      const clickX = (e.clientX - rect.left) / scale;
      const clickY = (e.clientY - rect.top) / scale;
      const gridX = Math.floor(clickX / tileSize);
      const gridY = Math.floor(clickY / tileSize);

      // Check if a token was clicked
      const clickedToken = mapData.tokens.find(
        (t) => t.x === gridX && t.y === gridY,
      );

      if (clickedToken) {
        setSelectedTokenId(clickedToken.id);
      } else if (selectedTokenId && onTokenMove) {
        // Move selected token to this position
        onTokenMove(selectedTokenId, gridX, gridY);
        setSelectedTokenId(null);
      } else {
        setSelectedTokenId(null);
      }
    },
    [mapData.tokens, onTokenMove, scale, selectedTokenId, tileSize],
  );

  return (
    <div
      ref={containerRef}
      data-testid="tile-grid-renderer"
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      <canvas
        ref={canvasRef}
        data-testid="tile-grid-canvas"
        onClick={handleCanvasClick}
        style={{
          width: `${mapPixelWidth * scale}px`,
          height: `${mapPixelHeight * scale}px`,
          imageRendering: "pixelated",
          cursor: selectedTokenId ? "crosshair" : "pointer",
        }}
      />
    </div>
  );
};

export default TileGridRenderer;
