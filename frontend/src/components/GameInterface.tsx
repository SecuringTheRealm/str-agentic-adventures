import type React from "react";
import { useEffect, useRef, useState } from "react";
import {
	type Campaign,
	type Character,
	type GameResponse,
	sendPlayerInput,
} from "../services/api";
import BattleMap from "./BattleMap";
import CharacterSheet from "./CharacterSheet";
import ChatBox from "./ChatBox";
import ImageDisplay from "./ImageDisplay";
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
	const [currentImage, setCurrentImage] = useState<string | null>(null);
	const [battleMapUrl, setBattleMapUrl] = useState<string | null>(null);
	const [combatActive, setCombatActive] = useState<boolean>(false);

	useEffect(() => {
		// Initial welcome message
		const welcomeMessage = `Welcome, ${character.name}! Your adventure in ${campaign.name} begins now. ${campaign.world_description || ""}`;
		setMessages([{ text: welcomeMessage, sender: "dm" }]);

		// Set initial world image if available
		if (campaign.world_art?.image_url) {
			setCurrentImage(campaign.world_art.image_url);
		}
	}, [character, campaign]);

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
				</div>

				<div className="center-panel">
					<ChatBox
						messages={messages}
						onSendMessage={handlePlayerInput}
						isLoading={loading}
					/>
				</div>

				<div className="right-panel">
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
