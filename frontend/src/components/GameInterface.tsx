import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useMediaQuery } from "../hooks/useMediaQuery";
import { useRealtimeVoice } from "../hooks/useRealtimeVoice";
import { useWebSocketSDK } from "../hooks/useWebSocketSDK";
import type { WebSocketMessage } from "../services/api";
import {
  generateBattleMap,
  generateImage,
  generateStructuredBattleMap,
  getOpeningNarrative,
  getVisualGenerationStatus,
  sendPlayerInput,
} from "../services/api";
import type { Campaign, Character, DiceResult } from "../types";
import type { BattleMapData } from "../types/battleMap";
import AutoSaveToast from "./AutoSaveToast";
import BattleMap from "./BattleMap";
import CharacterSheet from "./CharacterSheet";
import ChatBox from "./ChatBox";
import DiceRoller from "./DiceRoller";
import FloorRequestCard from "./FloorRequestCard";
import styles from "./GameInterface.module.css";
import ImageDisplay from "./ImageDisplay";
import MobileGameLayout from "./MobileGameLayout";

interface GameInterfaceProps {
  character: Character;
  campaign: Campaign;
}

// Utility function to extract user-friendly error messages from API errors
const extractErrorMessage = (
  error: unknown,
  fallbackMessage: string
): string => {
  if (error && typeof error === "object") {
    // Check for axios error response structure
    if (
      "response" in error &&
      error.response &&
      typeof error.response === "object"
    ) {
      const response = error.response as {
        data?: { detail?: string | Array<{ msg: string }> };
      };
      if (response.data?.detail) {
        if (typeof response.data.detail === "string") {
          return response.data.detail;
        }
        if (Array.isArray(response.data.detail)) {
          // Handle Pydantic validation errors which come as an array
          const messages = response.data.detail.map(
            (err: { msg: string }) => err.msg
          );
          return `Validation error: ${messages.join(", ")}`;
        }
      }
    }
    // Check for general error message
    else if ("message" in error && typeof (error as any).message === "string") {
      return (error as any).message;
    }
  }
  return fallbackMessage;
};

const GameInterface: React.FC<GameInterfaceProps> = ({
  character,
  campaign,
}) => {
  const isMobile = useMediaQuery("(max-width: 768px)");

  const [messages, setMessages] = useState<
    Array<{ text: string; sender: "player" | "dm" }>
  >([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [imageLoading, setImageLoading] = useState<boolean>(false);
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const [battleMapUrl, setBattleMapUrl] = useState<string | null>(null);
  const [battleMapData, setBattleMapData] = useState<BattleMapData | null>(
    null
  );
  const [combatActive, setCombatActive] = useState<boolean>(false);
  const [streamingMessage, setStreamingMessage] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [webSocketDiceResult, setWebSocketDiceResult] =
    useState<DiceResult | null>(null);
  const [suggestedActions, setSuggestedActions] = useState<string[]>([]);

  const voice = useRealtimeVoice();
  const [dmWantsFloor, setDmWantsFloor] = useState(false);

  // Stable session ID for image-generation budget tracking.
  // useRef ensures it never changes across re-renders.
  const sessionIdRef = useRef<string>(crypto.randomUUID());
  const sessionId = sessionIdRef.current;

  // How many more images the player can generate this session.
  // Initialised to null (unknown) and updated from the server response.
  const [imagesRemaining, setImagesRemaining] = useState<number | null>(null);

  // Add fallback mode when WebSocket isn't available
  const [useWebSocketFallback, setUseWebSocketFallback] =
    useState<boolean>(false);

  // Track the last auto-save timestamp to drive the AutoSaveToast
  const [lastAutoSave, setLastAutoSave] = useState<string | null>(null);
  const [imageGenerationAvailable, setImageGenerationAvailable] =
    useState<boolean>(true);
  const [imageGenerationStatusMessage, setImageGenerationStatusMessage] =
    useState<string | null>(null);

  const handleChatWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case "chat_start":
        setLoading(true);
        setIsStreaming(false);
        setStreamingMessage("");
        break;

      case "chat_typing":
        setLoading(true);
        setIsStreaming(false);
        break;

      case "chat_start_stream":
        setLoading(false);
        setIsStreaming(true);
        setStreamingMessage("");
        break;

      case "chat_stream":
        if (typeof message.chunk === "string") {
          setStreamingMessage(
            (typeof message.full_text === "string" ? message.full_text : "") ||
              ""
          );
        }
        break;

      case "chat_complete":
        setIsStreaming(false);
        setLoading(false);
        if (typeof message.message === "string") {
          setMessages((prev) => [
            ...prev,
            { text: message.message as string, sender: "dm" },
          ]);
        }
        setStreamingMessage("");
        break;

      case "chat_error":
        setIsStreaming(false);
        setLoading(false);
        setMessages((prev) => [
          ...prev,
          {
            text:
              typeof message.message === "string"
                ? message.message
                : "An error occurred processing your message.",
            sender: "dm",
          },
        ]);
        setStreamingMessage("");
        break;

      default:
        console.log("Unknown chat WebSocket message:", message);
    }
  };

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case "dice_result": {
        // Add dice result to chat
        const result =
          message.result && typeof message.result === "object"
            ? (message.result as { total?: number })
            : undefined;
        const diceMessage = `${message.player_name || "Player"} rolled ${message.notation || "dice"}: ${result?.total || "?"}`;
        setMessages((prev) => [...prev, { text: diceMessage, sender: "dm" }]);

        // Pass the dice result to the DiceRoller component
        setWebSocketDiceResult(message.result);
        // Clear it after a short delay to allow re-triggering if needed
        setTimeout(() => setWebSocketDiceResult(null), 100);
        break;
      }

      case "dm_narration":
        // DM narrates the outcome of the dice roll
        if (typeof message.narration === "string") {
          setMessages((prev) => [
            ...prev,
            { text: message.narration, sender: "dm" },
          ]);
        }
        break;

      case "game_update":
        // Handle game state updates
        if (message.update_type === "combat_start") {
          setCombatActive(true);
          // Attempt to load structured battle map data
          generateStructuredBattleMap(
            { location: "dungeon", terrain: "stone", size: "medium" },
            message.combat_context as object | undefined
          )
            .then((data) => setBattleMapData(data))
            .catch((err) =>
              console.warn("Structured battle map unavailable:", err)
            );
        } else if (message.update_type === "combat_end") {
          setCombatActive(false);
          setBattleMapData(null);
        }
        break;

      case "token_move":
        // Update token position from server
        if (
          battleMapData &&
          message.token_id &&
          message.x != null &&
          message.y != null
        ) {
          setBattleMapData((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              tokens: prev.tokens.map((t) =>
                t.id === message.token_id
                  ? { ...t, x: message.x as number, y: message.y as number }
                  : t
              ),
            };
          });
        }
        break;

      case "character_update":
        // Handle character updates (would need character state management)
        console.log("Character update received:", message);
        break;

      default:
        console.log("Unknown WebSocket message:", message);
    }
  };

  const { socket, isConnected } = useWebSocketSDK({
    connectionType: "campaign",
    campaignId: campaign.id!,
    onMessage: handleWebSocketMessage,
    onConnect: () => console.log("Connected to campaign WebSocket"),
    onDisconnect: () => console.log("Disconnected from campaign WebSocket"),
    onError: (error) => console.error("WebSocket error:", error),
  });

  const { socket: chatSocket, isConnected: chatConnected } = useWebSocketSDK({
    connectionType: "chat",
    campaignId: campaign.id!,
    onMessage: handleChatWebSocketMessage,
    onConnect: () => console.log("Connected to chat WebSocket"),
    onDisconnect: () => {
      console.log("Disconnected from chat WebSocket");
      setUseWebSocketFallback(true);
    },
    onError: (error) => {
      console.error("Chat WebSocket error:", error);
      setUseWebSocketFallback(true);
    },
  });

  // Fallback to REST API if WebSocket fails
  const effectiveChatConnected = chatConnected || useWebSocketFallback;

  useEffect(() => {
    // Set initial world image if available
    if (campaign.world_art?.image_url) {
      setCurrentImage(campaign.world_art.image_url);
    }

    // Fetch the opening narrative from the backend
    const fetchOpeningNarrative = async () => {
      if (!campaign.id) {
        // Fallback welcome message if no campaign id
        const welcomeMessage = `Welcome, ${character.name}! Your adventure in ${campaign.name} begins now. ${campaign.world_description || ""}`;
        setMessages([{ text: welcomeMessage.trim(), sender: "dm" }]);
        return;
      }

      setLoading(true);
      setMessages([
        {
          text: `Setting the scene for ${character.name}'s adventure…`,
          sender: "dm",
        },
      ]);
      try {
        const narrative = await getOpeningNarrative(campaign.id, {
          name: character.name,
          character_class: character.character_class,
          race: character.race,
          backstory: character.backstory ?? undefined,
        });

        const openingText = narrative.quest_hook
          ? `${narrative.scene_description}\n\n${narrative.quest_hook}`
          : narrative.scene_description;

        setMessages([{ text: openingText, sender: "dm" }]);
        setSuggestedActions(narrative.suggested_actions ?? []);
      } catch {
        // Fall back to a simple welcome message if the narrative call fails
        const welcomeMessage = `Welcome, ${character.name}! Your adventure in ${campaign.name} begins now. ${campaign.world_description || ""}`;
        setMessages([{ text: welcomeMessage.trim(), sender: "dm" }]);
      } finally {
        setLoading(false);
      }
    };

    fetchOpeningNarrative();
  }, [character, campaign]);

  useEffect(() => {
    let cancelled = false;

    const checkImageGenerationAvailability = async () => {
      try {
        const visualStatus = await getVisualGenerationStatus();
        if (cancelled) {
          return;
        }

        if (visualStatus.available) {
          setImageGenerationAvailable(true);
          setImageGenerationStatusMessage(null);
          return;
        }

        setImageGenerationAvailable(false);
        setImageGenerationStatusMessage(visualStatus.message);
      } catch (error) {
        console.warn("Failed to determine image generation availability:", error);
        if (!cancelled) {
          setImageGenerationAvailable(true);
          setImageGenerationStatusMessage(null);
        }
      }
    };

    checkImageGenerationAvailability();

    return () => {
      cancelled = true;
    };
  }, []);

  const showVisualError = useCallback(
    (title: string, fallbackMessage: string, error: unknown) => {
      const description = extractErrorMessage(error, fallbackMessage);
      toast.error(title, { description });
    },
    []
  );

  const markImageGenerationUnavailable = useCallback((message: string) => {
    setImageGenerationAvailable(false);
    setImageGenerationStatusMessage(message);
  }, []);

  const handleVisualGenerationUnavailable = useCallback(() => {
    if (imageGenerationStatusMessage) {
      toast.error("Visual generation unavailable", {
        description: imageGenerationStatusMessage,
      });
    }
  }, [imageGenerationStatusMessage]);

  const handleVisualGenerationSuccess = useCallback((message: string) => {
    toast.success(message);
  }, []);

  const handleGenerateCharacterPortrait = async () => {
    if (!imageGenerationAvailable) {
      handleVisualGenerationUnavailable();
      return;
    }

    // Validate character data exists
    if (!character?.name || !character?.race || !character?.character_class) {
      toast.error("Character portrait unavailable", {
        description:
          "Character information is incomplete. Add the missing details and try again.",
      });
      return;
    }

    setImageLoading(true);
    try {
      const portraitData = await generateImage({
        session_id: sessionId,
        image_type: "character_portrait",
        details: {
          name: character.name,
          race: character.race,
          class: character.character_class,
          // Add any additional character details for better portraits
        },
      });

      if (
        portraitData &&
        typeof portraitData === "object" &&
        "error" in portraitData &&
        typeof portraitData.error === "string"
      ) {
        markImageGenerationUnavailable(
          "Visual generation is unavailable because image generation is not configured."
        );
        throw new Error(portraitData.error);
      }

      if (
        portraitData &&
        typeof portraitData === "object" &&
        "image_url" in portraitData
      ) {
        const imageUrl = portraitData.image_url as string;
        if (imageUrl && typeof imageUrl === "string") {
          setCurrentImage(imageUrl);
          if (
            "images_remaining" in portraitData &&
            typeof portraitData.images_remaining === "number"
          ) {
            setImagesRemaining(portraitData.images_remaining);
          }
          handleVisualGenerationSuccess(
            `Character portrait generated for ${character.name}`
          );
        } else {
          throw new Error("Invalid image URL received from server");
        }
      } else {
        throw new Error("No image data received from server");
      }
    } catch (error) {
      console.error("Error generating character portrait:", error);
      showVisualError(
        "Character portrait failed",
        "Failed to generate character portrait. Please try again.",
        error
      );
    } finally {
      setImageLoading(false);
    }
  };

  const handleGenerateSceneIllustration = async () => {
    if (!imageGenerationAvailable) {
      handleVisualGenerationUnavailable();
      return;
    }

    setImageLoading(true);
    try {
      const sceneData = await generateImage({
        session_id: sessionId,
        image_type: "scene_illustration",
        details: {
          location: "fantasy tavern", // Default scene, could be dynamic
          mood: "atmospheric",
          time: "evening",
          notable_elements: ["wooden tables", "fireplace", "adventurers"],
        },
      });

      if (
        sceneData &&
        typeof sceneData === "object" &&
        "error" in sceneData &&
        typeof sceneData.error === "string"
      ) {
        markImageGenerationUnavailable(
          "Visual generation is unavailable because image generation is not configured."
        );
        throw new Error(sceneData.error);
      }

      if (
        sceneData &&
        typeof sceneData === "object" &&
        "image_url" in sceneData
      ) {
        const imageUrl = sceneData.image_url as string;
        if (imageUrl && typeof imageUrl === "string") {
          setCurrentImage(imageUrl);
          if (
            "images_remaining" in sceneData &&
            typeof sceneData.images_remaining === "number"
          ) {
            setImagesRemaining(sceneData.images_remaining);
          }
          handleVisualGenerationSuccess("Scene illustration generated");
        } else {
          throw new Error("Invalid image URL received from server");
        }
      } else {
        throw new Error("No image data received from server");
      }
    } catch (error) {
      console.error("Error generating scene illustration:", error);
      showVisualError(
        "Scene illustration failed",
        "Failed to generate scene illustration. Please try again.",
        error
      );
    } finally {
      setImageLoading(false);
    }
  };

  const handleGenerateBattleMap = async () => {
    if (!imageGenerationAvailable) {
      handleVisualGenerationUnavailable();
      return;
    }

    setImageLoading(true);
    try {
      const mapData = await generateBattleMap({
        session_id: sessionId,
        environment: {
          location: "dungeon corridor",
          terrain: "stone",
          size: "medium",
          features: ["pillars", "doorways", "torches"],
        },
      });

      if (
        mapData &&
        typeof mapData === "object" &&
        "error" in mapData &&
        typeof mapData.error === "string"
      ) {
        markImageGenerationUnavailable(
          "Visual generation is unavailable because image generation is not configured."
        );
        throw new Error(mapData.error);
      }

      if (mapData && typeof mapData === "object" && "image_url" in mapData) {
        const imageUrl = mapData.image_url as string;
        if (imageUrl && typeof imageUrl === "string") {
          setBattleMapUrl(imageUrl);
          setCombatActive(true);
          if (
            "images_remaining" in mapData &&
            typeof mapData.images_remaining === "number"
          ) {
            setImagesRemaining(mapData.images_remaining);
          }
          handleVisualGenerationSuccess("Tactical battle map generated");
        } else {
          throw new Error("Invalid map URL received from server");
        }
      } else {
        throw new Error("No map data received from server");
      }

      // Also attempt to load structured tile map data
      try {
        const structuredData = await generateStructuredBattleMap({
          location: "dungeon corridor",
          terrain: "stone",
          size: "medium",
          features: ["pillars", "doorways", "torches"],
        });
        setBattleMapData(structuredData);
      } catch (structuredError) {
        console.warn("Structured battle map unavailable:", structuredError);
      }
    } catch (error) {
      console.error("Error generating battle map:", error);
      showVisualError(
        "Battle map failed",
        "Failed to generate battle map. Please try again.",
        error
      );
    } finally {
      setImageLoading(false);
    }
  };

  const visualsDisabled =
    imageLoading || imagesRemaining === 0 || !imageGenerationAvailable;
  const visualsDisabledReason =
    imageGenerationStatusMessage ||
    (imagesRemaining === 0 ? "Image limit reached for this session." : null);

  const renderVisualButton = (
    label: string,
    onClick: () => Promise<void>,
    testId: string
  ) => {
    const button = (
      <Button
        variant="secondary"
        onClick={() => {
          void onClick();
        }}
        disabled={visualsDisabled}
        data-testid={testId}
      >
        {imageLoading ? "Generating..." : label}
      </Button>
    );

    if (!visualsDisabled || !visualsDisabledReason) {
      return button;
    }

    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={styles.visualButtonWrapper} tabIndex={0}>
            {button}
          </span>
        </TooltipTrigger>
        <TooltipContent>{visualsDisabledReason}</TooltipContent>
      </Tooltip>
    );
  };

  const handleTokenMove = useCallback(
    (tokenId: string, x: number, y: number) => {
      // Optimistic local update
      setBattleMapData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          tokens: prev.tokens.map((t) =>
            t.id === tokenId ? { ...t, x, y } : t
          ),
        };
      });

      // Send move via WebSocket
      if (isConnected && socket) {
        try {
          socket.send(
            JSON.stringify({
              type: "token_move",
              token_id: tokenId,
              x,
              y,
              campaign_id: campaign.id,
            })
          );
        } catch (err) {
          console.error("Failed to send token move:", err);
        }
      }
    },
    [campaign.id, isConnected, socket]
  );

  const handlePlayerInput = async (message: string) => {
    // Validate input before processing
    if (!message.trim()) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Please enter a message before sending.",
          sender: "dm",
        },
      ]);
      return;
    }

    // Validate required data exists
    if (!character?.id) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Character data is missing. Please refresh the page and try again.",
          sender: "dm",
        },
      ]);
      return;
    }

    if (!campaign?.id) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Campaign data is missing. Please refresh the page and try again.",
          sender: "dm",
        },
      ]);
      return;
    }

    // Check if chat WebSocket is connected or fallback is enabled
    if (!effectiveChatConnected && !chatSocket) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Chat connection is not available. Please wait and try again.",
          sender: "dm",
        },
      ]);
      return;
    }

    // Add player message to chat and clear suggested actions
    setMessages((prev) => [...prev, { text: message, sender: "player" }]);
    setSuggestedActions([]);

    // Try WebSocket first, fallback to REST API
    if (chatConnected && chatSocket) {
      // Send message via WebSocket for streaming response
      const chatMessage = {
        type: "chat_input",
        message: message.trim(),
        character_id: character.id,
        campaign_id: campaign.id,
      };

      try {
        chatSocket.send(JSON.stringify(chatMessage));
      } catch (error) {
        console.error("Error sending chat message:", error);
        // Fallback to REST API
        await handleRestApiMessage(message);
      }
    } else {
      // Use REST API fallback
      await handleRestApiMessage(message);
    }

    // If voice is connected, also send the text to the realtime session for context
    if (voice.voiceEnabled && voice.connectionState === "connected") {
      voice.sendTextAsVoiceContext(message);
    }
  };

  const handleRestApiMessage = async (message: string) => {
    try {
      setLoading(true);

      const response = await sendPlayerInput({
        character_id: character.id!,
        campaign_id: campaign.id!,
        message: message.trim(),
      });

      if (response.message) {
        setMessages((prev) => [
          ...prev,
          {
            text: response.message,
            sender: "dm",
          },
        ]);
      }

      // Handle visuals if present
      if (response.images && response.images.length > 0) {
        const imageUrl = response.images[0];
        if (imageUrl) {
          setCurrentImage(imageUrl);
        }
      }

      // Handle combat updates if present
      if (response.combat_updates) {
        if (response.combat_updates.status === "active") {
          setCombatActive(true);
          if (response.combat_updates.map_url) {
            setBattleMapUrl(response.combat_updates.map_url);
          }
        } else if (response.combat_updates.status === "inactive") {
          setCombatActive(false);
          setBattleMapUrl(null);
        }
      }

      // Show auto-save notification when the backend reports a save
      if (
        response.state_updates?.auto_saved &&
        response.state_updates?.last_auto_save
      ) {
        setLastAutoSave(response.state_updates.last_auto_save as string);
      }
    } catch (error) {
      console.error("Error with REST API fallback:", error);
      const errorMessage = extractErrorMessage(
        error,
        "Failed to process your message. Please try again."
      );
      setMessages((prev) => [
        ...prev,
        {
          text: errorMessage,
          sender: "dm",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDiceRoll = useCallback(
    (result: DiceResult) => {
      if (!isConnected) {
        const diceMessage = `You rolled ${result.notation}: ${result.total}`;
        setMessages((prev) => [
          ...prev,
          { text: diceMessage, sender: "player" },
        ]);
      }
    },
    [isConnected]
  );

  if (isMobile) {
    return (
      <div className={styles.gameInterface} data-testid="game-interface">
        <AutoSaveToast lastAutoSave={lastAutoSave} />
        <MobileGameLayout
          character={character}
          campaign={campaign}
          messages={messages}
          onSendMessage={handlePlayerInput}
          isLoading={loading}
          streamingMessage={isStreaming ? streamingMessage : undefined}
          suggestedActions={suggestedActions}
          onSuggestedAction={handlePlayerInput}
          currentImage={currentImage}
          battleMapUrl={battleMapUrl}
          combatActive={combatActive}
          imageLoading={imageLoading}
          imagesRemaining={imagesRemaining}
          imageGenerationAvailable={imageGenerationAvailable}
          imageGenerationStatusMessage={imageGenerationStatusMessage}
          onGeneratePortrait={handleGenerateCharacterPortrait}
          onGenerateScene={handleGenerateSceneIllustration}
          onGenerateBattleMap={handleGenerateBattleMap}
          diceRollerProps={{
            characterId: character.id,
            playerName: character.name,
            websocket: socket,
            webSocketDiceResult: webSocketDiceResult,
            onRoll: handleDiceRoll,
          }}
        />
      </div>
    );
  }

  return (
    <div className={styles.gameInterface} data-testid="game-interface">
      <AutoSaveToast lastAutoSave={lastAutoSave} />
      <div className={styles.gameContainer}>
        <aside aria-label="Character sheet" className={styles.leftPanel}>
          <CharacterSheet character={character} />
          <DiceRoller
            characterId={character.id}
            playerName={character.name}
            websocket={socket}
            webSocketDiceResult={webSocketDiceResult}
            onRoll={handleDiceRoll}
          />
        </aside>

        <main aria-label="Game chat" className={styles.centerPanel}>
          <ChatBox
            messages={messages}
            onSendMessage={handlePlayerInput}
            isLoading={loading}
            streamingMessage={isStreaming ? streamingMessage : undefined}
            suggestedActions={suggestedActions}
            onSuggestedAction={handlePlayerInput}
            voiceEnabled={voice.voiceEnabled}
            isSpeaking={voice.isSpeaking}
            isListening={voice.isListening}
            onMicPressStart={voice.startListening}
            onMicPressEnd={voice.stopListening}
          />
          <Button
            variant={voice.voiceEnabled ? "default" : "outline"}
            size="sm"
            onClick={() => {
              if (voice.voiceEnabled) {
                voice.disconnect();
              } else {
                voice.connect();
              }
            }}
            aria-label={voice.voiceEnabled ? "Disable voice" : "Enable voice"}
          >
            {voice.connectionState === "connecting"
              ? "Connecting..."
              : voice.voiceEnabled
                ? "Voice On"
                : "Voice Off"}
          </Button>
        </main>

        <aside
          aria-label="Visuals and battle map"
          className={styles.rightPanel}
        >
          <FloorRequestCard
            visible={dmWantsFloor}
            onGrantFloor={() => setDmWantsFloor(false)}
          />
          <TooltipProvider delayDuration={150}>
            <div className={styles.visualControls}>
              <h4>Generate Visuals</h4>
              {imageGenerationStatusMessage && (
                <div
                  className={styles.visualStatus}
                  role="status"
                  data-testid="visual-generation-status"
                >
                  {imageGenerationStatusMessage}
                </div>
              )}
              {imagesRemaining !== null && (
                <p className={styles.imageBudget}>
                  {imagesRemaining > 0
                    ? `${imagesRemaining} illustration${imagesRemaining === 1 ? "" : "s"} remaining this session`
                    : "Image limit reached for this session"}
                </p>
              )}
              <div className={styles.visualButtons}>
                {renderVisualButton(
                  "Character Portrait",
                  handleGenerateCharacterPortrait,
                  "generate-portrait-button"
                )}
                {renderVisualButton(
                  "Scene Illustration",
                  handleGenerateSceneIllustration,
                  "generate-scene-button"
                )}
                {renderVisualButton(
                  "Battle Map",
                  handleGenerateBattleMap,
                  "generate-battle-map-button"
                )}
              </div>
            </div>
          </TooltipProvider>

          <div className={styles.imageSection}>
            <ImageDisplay imageUrl={currentImage} />
          </div>

          {combatActive && (
            <div className={styles.battleMapSection}>
              <BattleMap
                mapUrl={battleMapUrl}
                mapData={battleMapData}
                onTokenMove={handleTokenMove}
              />
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};

export default GameInterface;
