import type React from "react";
import { useEffect, useState } from "react";
import {
	type Campaign,
	type Character,
	generateImage,
	generateBattleMap,
	sendPlayerInput,
} from "../services/api";
import { getCampaignWebSocketUrl, getChatWebSocketUrl } from "../utils/urls";
import BattleMap from "./BattleMap";
import CharacterSheet from "./CharacterSheet";
import ChatBox from "./ChatBox";
import ImageDisplay from "./ImageDisplay";
import DiceRoller from "./DiceRoller";
import { useWebSocket, type WebSocketMessage } from "../hooks/useWebSocket";
import "./GameInterface.css";

interface GameInterfaceProps {
	character: Character;
	campaign: Campaign;
}

// Utility function to extract user-friendly error messages from API errors
const extractErrorMessage = (error: unknown, fallbackMessage: string): string => {
	if (error && typeof error === 'object') {
		// Check for axios error response structure
		if ('response' in error && error.response && typeof error.response === 'object') {
			const response = error.response as { data?: { detail?: string | Array<{ msg: string }> } };
			if (response.data?.detail) {
				if (typeof response.data.detail === 'string') {
					return response.data.detail;
				} else if (Array.isArray(response.data.detail)) {
					// Handle Pydantic validation errors which come as an array
					const messages = response.data.detail.map((err: { msg: string }) => err.msg);
					return `Validation error: ${messages.join(', ')}`;
				}
			}
		}
		// Check for general error message
		else if ('message' in error && typeof (error as any).message === 'string') {
			return (error as any).message;
		}
	}
	return fallbackMessage;
};

const GameInterface: React.FC<GameInterfaceProps> = ({
	character,
	campaign,
}) => {
	const [messages, setMessages] = useState<
		Array<{ text: string; sender: "player" | "dm" }>
	>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [imageLoading, setImageLoading] = useState<boolean>(false);
	const [currentImage, setCurrentImage] = useState<string | null>(null);
	const [battleMapUrl, setBattleMapUrl] = useState<string | null>(null);
	const [combatActive, setCombatActive] = useState<boolean>(false);
	const [streamingMessage, setStreamingMessage] = useState<string>("");
	const [isStreaming, setIsStreaming] = useState<boolean>(false);
	const [webSocketDiceResult, setWebSocketDiceResult] = useState<any>(null);

	// WebSocket integration for campaign updates (non-chat)
	const wsUrl = getCampaignWebSocketUrl(campaign.id);
	// WebSocket integration for chat streaming  
	const chatWsUrl = getChatWebSocketUrl(campaign.id);

	// Add fallback mode when WebSocket isn't available
	const [useWebSocketFallback, setUseWebSocketFallback] = useState<boolean>(false);

	const handleChatWebSocketMessage = (message: WebSocketMessage) => {
		switch (message.type) {
			case 'chat_start':
				setLoading(true);
				setIsStreaming(false);
				setStreamingMessage("");
				break;

			case 'chat_typing':
				setLoading(true);
				setIsStreaming(false);
				break;

			case 'chat_start_stream':
				setLoading(false);
				setIsStreaming(true);
				setStreamingMessage("");
				break;

			case 'chat_stream':
				if (typeof message.chunk === 'string') {
					setStreamingMessage(message.full_text || "");
				}
				break;

			case 'chat_complete':
				setIsStreaming(false);
				setLoading(false);
				if (message.message) {
					setMessages(prev => [...prev, { text: message.message, sender: 'dm' }]);
				}
				setStreamingMessage("");
				break;

			case 'chat_error':
				setIsStreaming(false);
				setLoading(false);
				setMessages(prev => [...prev, { 
					text: message.message || "An error occurred processing your message.", 
					sender: 'dm' 
				}]);
				setStreamingMessage("");
				break;

			default:
				console.log('Unknown chat WebSocket message:', message);
		}
	};

	const handleWebSocketMessage = (message: WebSocketMessage) => {
		switch (message.type) {
			case 'dice_result':
				// Add dice result to chat
				const diceMessage = `${message.player_name} rolled ${message.notation}: ${message.result.total}`;
				setMessages(prev => [...prev, { text: diceMessage, sender: 'dm' }]);
				
				// Pass the dice result to the DiceRoller component
				setWebSocketDiceResult(message.result);
				// Clear it after a short delay to allow re-triggering if needed
				setTimeout(() => setWebSocketDiceResult(null), 100);
				break;

			case 'game_update':
				// Handle game state updates
				if (message.update_type === 'combat_start') {
					setCombatActive(true);
				} else if (message.update_type === 'combat_end') {
					setCombatActive(false);
				}
				break;

			case 'character_update':
				// Handle character updates (would need character state management)
				console.log('Character update received:', message);
				break;

			default:
				console.log('Unknown WebSocket message:', message);
		}
	};

	const { socket, isConnected } = useWebSocket(wsUrl, {
		onMessage: handleWebSocketMessage,
		onConnect: () => console.log('Connected to campaign WebSocket'),
		onDisconnect: () => console.log('Disconnected from campaign WebSocket'),
		onError: (error) => console.error('WebSocket error:', error)
	});

	const { socket: chatSocket, isConnected: chatConnected } = useWebSocket(chatWsUrl, {
		onMessage: handleChatWebSocketMessage,
		onConnect: () => console.log('Connected to chat WebSocket'),
		onDisconnect: () => {
			console.log('Disconnected from chat WebSocket');
			setUseWebSocketFallback(true);
		},
		onError: (error) => {
			console.error('Chat WebSocket error:', error);
			setUseWebSocketFallback(true);
		}
	});

	// Fallback to REST API if WebSocket fails
	const effectiveChatConnected = chatConnected || useWebSocketFallback;

	useEffect(() => {
		// Initial welcome message
		const welcomeMessage = `Welcome, ${character.name}! Your adventure in ${campaign.name} begins now. ${campaign.world_description || ""}`;
		setMessages([{ text: welcomeMessage, sender: "dm" }]);

		// Set initial world image if available
		if (campaign.world_art?.image_url) {
			setCurrentImage(campaign.world_art.image_url);
		}
	}, [character, campaign]);

	const handleGenerateCharacterPortrait = async () => {
		// Validate character data exists
		if (!character?.name || !character?.race || !character?.character_class) {
			setMessages(prev => [...prev, {
				text: "Character information is incomplete. Cannot generate portrait.",
				sender: "dm"
			}]);
			return;
		}

		setImageLoading(true);
		try {
			const portraitData = await generateImage({
				image_type: "character_portrait",
				details: {
					name: character.name,
					race: character.race,
					class: character.character_class,
					// Add any additional character details for better portraits
				}
			});

			if (portraitData && typeof portraitData === 'object' && 'image_url' in portraitData) {
				const imageUrl = portraitData.image_url as string;
				if (imageUrl && typeof imageUrl === 'string') {
					setCurrentImage(imageUrl);
					setMessages(prev => [...prev, {
						text: `Generated character portrait for ${character.name}`,
						sender: "dm"
					}]);
				} else {
					throw new Error('Invalid image URL received from server');
				}
			} else {
				throw new Error('No image data received from server');
			}
		} catch (error) {
			console.error("Error generating character portrait:", error);
			const errorMessage = extractErrorMessage(error, "Failed to generate character portrait. Please try again.");
			setMessages(prev => [...prev, {
				text: errorMessage,
				sender: "dm"
			}]);
		} finally {
			setImageLoading(false);
		}
	};

	const handleGenerateSceneIllustration = async () => {
		setImageLoading(true);
		try {
			const sceneData = await generateImage({
				image_type: "scene_illustration",
				details: {
					location: "fantasy tavern", // Default scene, could be dynamic
					mood: "atmospheric",
					time: "evening",
					notable_elements: ["wooden tables", "fireplace", "adventurers"]
				}
			});

			if (sceneData && typeof sceneData === 'object' && 'image_url' in sceneData) {
				const imageUrl = sceneData.image_url as string;
				if (imageUrl && typeof imageUrl === 'string') {
					setCurrentImage(imageUrl);
					setMessages(prev => [...prev, {
						text: "Generated scene illustration",
						sender: "dm"
					}]);
				} else {
					throw new Error('Invalid image URL received from server');
				}
			} else {
				throw new Error('No image data received from server');
			}
		} catch (error) {
			console.error("Error generating scene illustration:", error);
			const errorMessage = extractErrorMessage(error, "Failed to generate scene illustration. Please try again.");
			setMessages(prev => [...prev, {
				text: errorMessage,
				sender: "dm"
			}]);
		} finally {
			setImageLoading(false);
		}
	};

	const handleGenerateBattleMap = async () => {
		setImageLoading(true);
		try {
			const mapData = await generateBattleMap({
				environment: {
					location: "dungeon corridor",
					terrain: "stone",
					size: "medium",
					features: ["pillars", "doorways", "torches"]
				}
			});

			if (mapData && typeof mapData === 'object' && 'image_url' in mapData) {
				const imageUrl = mapData.image_url as string;
				if (imageUrl && typeof imageUrl === 'string') {
					setBattleMapUrl(imageUrl);
					setCombatActive(true);
					setMessages(prev => [...prev, {
						text: "Generated tactical battle map",
						sender: "dm"
					}]);
				} else {
					throw new Error('Invalid map URL received from server');
				}
			} else {
				throw new Error('No map data received from server');
			}
		} catch (error) {
			console.error("Error generating battle map:", error);
			const errorMessage = extractErrorMessage(error, "Failed to generate battle map. Please try again.");
			setMessages(prev => [...prev, {
				text: errorMessage,
				sender: "dm"
			}]);
		} finally {
			setImageLoading(false);
		}
	};

	const handlePlayerInput = async (message: string) => {
		// Validate input before processing
		if (!message.trim()) {
			setMessages((prev) => [...prev, { 
				text: "Please enter a message before sending.", 
				sender: "dm" 
			}]);
			return;
		}

		// Validate required data exists
		if (!character?.id) {
			setMessages((prev) => [...prev, { 
				text: "Character data is missing. Please refresh the page and try again.", 
				sender: "dm" 
			}]);
			return;
		}

		if (!campaign?.id) {
			setMessages((prev) => [...prev, { 
				text: "Campaign data is missing. Please refresh the page and try again.", 
				sender: "dm" 
			}]);
			return;
		}

		// Check if chat WebSocket is connected or fallback is enabled
		if (!effectiveChatConnected && !chatSocket) {
			setMessages((prev) => [...prev, { 
				text: "Chat connection is not available. Please wait and try again.", 
				sender: "dm" 
			}]);
			return;
		}

		// Add player message to chat
		setMessages((prev) => [...prev, { text: message, sender: "player" }]);
		
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
	};

	const handleRestApiMessage = async (message: string) => {
		try {
			setLoading(true);
			
			const response = await sendPlayerInput({
				character_id: character.id,
				campaign_id: campaign.id,
				message: message.trim(),
			});

			if (response.message) {
				setMessages((prev) => [...prev, { 
					text: response.message, 
					sender: "dm" 
				}]);
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
				if (response.combat_updates.status === 'active') {
					setCombatActive(true);
					if (response.combat_updates.map_url) {
						setBattleMapUrl(response.combat_updates.map_url);
					}
				} else if (response.combat_updates.status === 'inactive') {
					setCombatActive(false);
					setBattleMapUrl(null);
				}
			}

		} catch (error) {
			console.error("Error with REST API fallback:", error);
			const errorMessage = extractErrorMessage(error, "Failed to process your message. Please try again.");
			setMessages((prev) => [...prev, {
				text: errorMessage,
				sender: "dm",
			}]);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="game-interface">
			<div className="game-container">
				<div className="left-panel">
					<CharacterSheet character={character} />
					<DiceRoller
						characterId={character.id}
						playerName={character.name}
						websocket={socket}
						webSocketDiceResult={webSocketDiceResult}
						onRoll={(result) => {
							// Add dice roll to local chat if not using WebSocket
							if (!isConnected) {
								const diceMessage = `You rolled ${result.notation}: ${result.total}`;
								setMessages(prev => [...prev, { text: diceMessage, sender: 'player' }]);
							}
						}}
					/>
				</div>

				<div className="center-panel">
					<ChatBox
						messages={messages}
						onSendMessage={handlePlayerInput}
						isLoading={loading}
						streamingMessage={isStreaming ? streamingMessage : undefined}
					/>
				</div>

				<div className="right-panel">
					<div className="visual-controls">
						<h4>Generate Visuals</h4>
						<div className="visual-buttons">
							<button
								onClick={handleGenerateCharacterPortrait}
								disabled={imageLoading}
								className="visual-button"
							>
								{imageLoading ? "Generating..." : "Character Portrait"}
							</button>
							<button
								onClick={handleGenerateSceneIllustration}
								disabled={imageLoading}
								className="visual-button"
							>
								{imageLoading ? "Generating..." : "Scene Illustration"}
							</button>
							<button
								onClick={handleGenerateBattleMap}
								disabled={imageLoading}
								className="visual-button"
							>
								{imageLoading ? "Generating..." : "Battle Map"}
							</button>
						</div>
					</div>

					<div className="image-section">
						<ImageDisplay imageUrl={currentImage} />
					</div>

					{combatActive && (
						<div className="battle-map-section">
							<BattleMap mapUrl={battleMapUrl} />
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

export default GameInterface;
