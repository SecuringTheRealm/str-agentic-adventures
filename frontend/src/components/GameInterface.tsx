import type React from "react";
import { useEffect, useRef, useState } from "react";
import {
	type Campaign,
	type Character,
	type GameResponse,
	sendPlayerInput,
	generateImage,
	generateBattleMap,
} from "../services/api";
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

	// WebSocket integration for real-time updates
	const wsUrl = `${(process.env.REACT_APP_WS_URL || 'ws://localhost:8000').replace('http', 'ws')}/api/ws/${campaign.id}`;
	
	const handleWebSocketMessage = (message: WebSocketMessage) => {
		switch (message.type) {
			case 'dice_result':
				// Add dice result to chat
				const diceMessage = `${message.player_name} rolled ${message.notation}: ${message.result.total}`;
				setMessages(prev => [...prev, { text: diceMessage, sender: 'dm' }]);
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

	const { socket, isConnected, sendMessage } = useWebSocket(wsUrl, {
		onMessage: handleWebSocketMessage,
		onConnect: () => console.log('Connected to campaign WebSocket'),
		onDisconnect: () => console.log('Disconnected from campaign WebSocket'),
		onError: (error) => console.error('WebSocket error:', error)
	});

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
				setCurrentImage(portraitData.image_url as string);
				setMessages(prev => [...prev, { 
					text: `Generated character portrait for ${character.name}`, 
					sender: "dm" 
				}]);
			}
		} catch (error) {
			console.error("Error generating character portrait:", error);
			setMessages(prev => [...prev, { 
				text: "Failed to generate character portrait. Please try again.", 
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
				setCurrentImage(sceneData.image_url as string);
				setMessages(prev => [...prev, { 
					text: "Generated scene illustration", 
					sender: "dm" 
				}]);
			}
		} catch (error) {
			console.error("Error generating scene illustration:", error);
			setMessages(prev => [...prev, { 
				text: "Failed to generate scene illustration. Please try again.", 
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
				setBattleMapUrl(mapData.image_url as string);
				setCombatActive(true);
				setMessages(prev => [...prev, { 
					text: "Generated tactical battle map", 
					sender: "dm" 
				}]);
			}
		} catch (error) {
			console.error("Error generating battle map:", error);
			setMessages(prev => [...prev, { 
				text: "Failed to generate battle map. Please try again.", 
				sender: "dm" 
			}]);
		} finally {
			setImageLoading(false);
		}
	};

	const handlePlayerInput = async (message: string) => {
		// Add player message to chat
		setMessages((prev) => [...prev, { text: message, sender: "player" }]);
		setLoading(true);

		try {
			// Send message to API
			const response = await sendPlayerInput({
				message,
				character_id: character.id,
				campaign_id: campaign.id,
			});

			// Add DM response to chat
			setMessages((prev) => [
				...prev,
				{ text: response.message, sender: "dm" },
			]);

			// Update images if provided
			if (response.images && response.images.length > 0) {
				setCurrentImage(response.images[0]);
			}

			// Handle combat updates
			if (response.combat_updates) {
				setCombatActive(response.combat_updates.status === "active");

				// Set battle map if available
				if (response.combat_updates.map_url) {
					setBattleMapUrl(response.combat_updates.map_url);
				}
			}
		} catch (error) {
			console.error("Error processing player input:", error);
			setMessages((prev) => [
				...prev,
				{
					text: "Something went wrong. Please try again.",
					sender: "dm",
				},
			]);
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
