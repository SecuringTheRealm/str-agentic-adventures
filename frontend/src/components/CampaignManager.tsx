import React, { useState, useEffect } from 'react';
import { useWebSocket, type WebSocketMessage } from '../hooks/useWebSocket';
import { getCampaignWebSocketUrl } from '../utils/urls';
import type { Campaign, Character } from '../services/api';
import './CampaignManager.css';

interface Player {
	id: string;
	name: string;
	character_id?: string;
	connected: boolean;
	last_seen: string;
}

interface CampaignManagerProps {
	campaign: Campaign;
	currentPlayer: {
		id: string;
		name: string;
		character?: Character;
	};
	onPlayerJoin?: (player: Player) => void;
	onPlayerLeave?: (playerId: string) => void;
	onChatMessage?: (message: string, sender: string) => void;
}

const CampaignManager: React.FC<CampaignManagerProps> = ({
	campaign,
	currentPlayer,
	onPlayerJoin,
	onPlayerLeave,
	onChatMessage
}) => {
	const [connectedPlayers, setConnectedPlayers] = useState<Player[]>([]);
	const [chatMessage, setChatMessage] = useState('');
	const [showPlayerList, setShowPlayerList] = useState(false);
	const [isSessionActive, setIsSessionActive] = useState(false);

	// WebSocket for campaign-wide communication
	const wsUrl = getCampaignWebSocketUrl(campaign.id);

	const handleWebSocketMessage = (message: WebSocketMessage) => {
		switch (message.type) {
			case 'player_joined':
				const newPlayer: Player = {
					id: message.player_id,
					name: message.player_name,
					character_id: message.character_id,
					connected: true,
					last_seen: new Date().toISOString()
				};
				setConnectedPlayers(prev => {
					const existing = prev.find(p => p.id === newPlayer.id);
					if (existing) {
						return prev.map(p => p.id === newPlayer.id ? { ...p, connected: true, last_seen: newPlayer.last_seen } : p);
					}
					return [...prev, newPlayer];
				});
				if (onPlayerJoin) {
					onPlayerJoin(newPlayer);
				}
				break;

			case 'player_left':
				setConnectedPlayers(prev =>
					prev.map(p =>
						p.id === message.player_id
							? { ...p, connected: false, last_seen: new Date().toISOString() }
							: p
					)
				);
				if (onPlayerLeave) {
					onPlayerLeave(message.player_id);
				}
				break;

			case 'chat_message':
				if (onChatMessage) {
					onChatMessage(message.content, message.sender_name);
				}
				break;

			case 'session_update':
				setIsSessionActive(message.status === 'active');
				break;

			case 'dice_result':
				// Handled by parent components
				break;

			default:
				console.log('Unhandled campaign message:', message);
		}
	};

	const { socket, isConnected, sendMessage } = useWebSocket(wsUrl, {
		onMessage: handleWebSocketMessage,
		onConnect: () => {
			console.log('Connected to campaign');
			// Announce our presence
			sendMessage({
				type: 'player_join',
				player_id: currentPlayer.id,
				player_name: currentPlayer.name,
				character_id: currentPlayer.character?.id,
				timestamp: new Date().toISOString()
			});
		},
		onDisconnect: () => {
			console.log('Disconnected from campaign');
		}
	});

	// Send chat message
	const handleSendChat = () => {
		if (!chatMessage.trim() || !isConnected) return;

		sendMessage({
			type: 'chat_message',
			content: chatMessage,
			sender_id: currentPlayer.id,
			sender_name: currentPlayer.name,
			character_id: currentPlayer.character?.id,
			timestamp: new Date().toISOString()
		});

		setChatMessage('');
	};

	// Start/stop session
	const handleSessionToggle = () => {
		if (!isConnected) return;

		sendMessage({
			type: 'session_control',
			action: isSessionActive ? 'stop' : 'start',
			campaign_id: campaign.id,
			player_id: currentPlayer.id,
			timestamp: new Date().toISOString()
		});
	};

	// Invite player (simulated - would integrate with actual invite system)
	const handleInvitePlayer = () => {
		const inviteCode = `${campaign.id}-${Date.now()}`;

		// Copy invite link to clipboard
		const inviteLink = `${window.location.origin}/join/${inviteCode}`;
		navigator.clipboard.writeText(inviteLink).then(() => {
			alert(`Invite link copied to clipboard: ${inviteLink}`);
		}).catch(() => {
			alert(`Invite Code: ${inviteCode}\nShare this with other players to invite them to the campaign.`);
		});
	};

	return (
		<div className="campaign-manager">
			<div className="campaign-header">
				<div className="campaign-info">
					<h3>{campaign.name}</h3>
					<div className="campaign-meta">
						<span className="setting">{campaign.setting}</span>
						<span className="tone">{campaign.tone}</span>
						<span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
							{isConnected ? '🟢 Connected' : '🔴 Disconnected'}
						</span>
					</div>
				</div>

				<div className="campaign-controls">
					<button
						onClick={() => setShowPlayerList(!showPlayerList)}
						className="player-list-toggle"
					>
						👥 Players ({connectedPlayers.filter(p => p.connected).length})
					</button>

					<button
						onClick={handleInvitePlayer}
						className="invite-button"
					>
						📧 Invite
					</button>

					<button
						onClick={handleSessionToggle}
						className={`session-toggle ${isSessionActive ? 'active' : 'inactive'}`}
						disabled={!isConnected}
					>
						{isSessionActive ? '⏸️ Pause Session' : '▶️ Start Session'}
					</button>
				</div>
			</div>

			{showPlayerList && (
				<div className="player-list">
					<h4>Connected Players:</h4>
					{connectedPlayers.length === 0 ? (
						<p className="no-players">No other players connected</p>
					) : (
						<div className="player-grid">
							{connectedPlayers.map((player) => (
								<div key={player.id} className={`player-card ${player.connected ? 'online' : 'offline'}`}>
									<div className="player-info">
										<div className="player-name">{player.name}</div>
										{player.character_id && (
											<div className="player-character">Playing as Character</div>
										)}
										<div className="player-status">
											{player.connected ? '🟢 Online' : '🔴 Offline'}
										</div>
									</div>
									<div className="last-seen">
										{player.connected
											? 'Active now'
											: `Last seen: ${new Date(player.last_seen).toLocaleTimeString()}`
										}
									</div>
								</div>
							))}
						</div>
					)}
				</div>
			)}

			{/* Quick chat for coordination */}
			<div className="quick-chat">
				<div className="chat-input">
					<input
						type="text"
						value={chatMessage}
						onChange={(e) => setChatMessage(e.target.value)}
						onKeyPress={(e) => e.key === 'Enter' && handleSendChat()}
						placeholder="Send a quick message to other players..."
						disabled={!isConnected}
						className="chat-message-input"
					/>
					<button
						onClick={handleSendChat}
						disabled={!chatMessage.trim() || !isConnected}
						className="send-chat-button"
					>
						📤
					</button>
				</div>
			</div>

			{isSessionActive && (
				<div className="session-active-indicator">
					<div className="pulse-indicator">🎲</div>
					<span>Game Session Active</span>
				</div>
			)}
		</div>
	);
};

export default CampaignManager;