import React, { useState, useCallback, useEffect } from 'react';
import styles from "./DiceRoller.module.css";
import { apiClient } from '../services/api';

interface DiceResult {
	notation: string;
	rolls: number[];
	total: number;
	modifier?: number;
	dropped?: number[];
	rerolls?: Array<{
		original: number;
		new: number;
		index: number;
	}>;
	character_bonus?: number;
	timestamp: string;
}

interface DiceRollerProps {
	onRoll?: (result: DiceResult) => void;
	characterId?: string;
	playerName?: string;
	websocket?: WebSocket | null;
	webSocketDiceResult?: DiceResult | null;
}

const DiceRoller: React.FC<DiceRollerProps> = ({ onRoll, characterId, playerName, websocket, webSocketDiceResult }) => {
	const [notation, setNotation] = useState('1d20');
	const [skill, setSkill] = useState('');
	const [isRolling, setIsRolling] = useState(false);
	const [lastResult, setLastResult] = useState<DiceResult | null>(null);
	const [rollHistory, setRollHistory] = useState<DiceResult[]>([]);

	// Handle WebSocket dice results
	const completeWebSocketDiceRoll = useCallback((result: DiceResult) => {
		// Add timestamp if not present
		if (!result.timestamp) {
			result.timestamp = new Date().toISOString();
		}

		setLastResult(result);
		setRollHistory(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 rolls
		setIsRolling(false);

		if (onRoll) {
			onRoll(result);
		}
	}, [onRoll]);

	// Handle WebSocket dice results when they come in
	useEffect(() => {
		if (webSocketDiceResult && isRolling) {
			completeWebSocketDiceRoll(webSocketDiceResult);
		}
	}, [webSocketDiceResult, isRolling, completeWebSocketDiceRoll]);

	const commonRolls = [
		{ label: 'd20', notation: '1d20' },
		{ label: 'd12', notation: '1d12' },
		{ label: 'd10', notation: '1d10' },
		{ label: 'd8', notation: '1d8' },
		{ label: 'd6', notation: '1d6' },
		{ label: 'd4', notation: '1d4' },
		{ label: 'Advantage', notation: '2d20kh1' },
		{ label: 'Disadvantage', notation: '2d20kl1' },
		{ label: 'Stats (4d6dl1)', notation: '4d6dl1' },
	];

	const skillOptions = [
		'athletics', 'acrobatics', 'sleight_of_hand', 'stealth',
		'arcana', 'history', 'investigation', 'nature', 'religion',
		'animal_handling', 'insight', 'medicine', 'perception', 'survival',
		'deception', 'intimidation', 'performance', 'persuasion'
	];

	const rollDice = useCallback(async (diceNotation: string = notation) => {
		setIsRolling(true);

		try {
			let result: DiceResult;

			if (websocket && websocket.readyState === WebSocket.OPEN) {
				// Send dice roll via WebSocket for real-time updates
				const message = {
					type: 'dice_roll',
					notation: diceNotation,
					character_id: characterId,
					skill: skill || undefined,
					player_name: playerName || 'Player',
					timestamp: new Date().toISOString()
				};
				websocket.send(JSON.stringify(message));
				return; // WebSocket will handle the response
			} else {
				// Fallback to direct API call
				const endpoint = characterId && skill
					? '/game/dice/roll-with-character'
					: '/game/dice/roll';

				const requestBody = characterId && skill ? {
					notation: diceNotation,
					character_id: characterId,
					skill: skill
				} : {
					notation: diceNotation
				};

				const response = await apiClient.post(endpoint, requestBody);
				result = response.data;
			}

			// Add timestamp if not present
			if (!result.timestamp) {
				result.timestamp = new Date().toISOString();
			}

			setLastResult(result);
			setRollHistory(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 rolls

			if (onRoll) {
				onRoll(result);
			}
		} catch (error) {
			console.error('Error rolling dice:', error);
			alert('Failed to roll dice. Please try again.');
		} finally {
			setIsRolling(false);
		}
	}, [notation, skill, characterId, playerName, websocket, onRoll]);

	const formatResult = (result: DiceResult) => {
		const parts = [];

		// Show individual rolls
		if (result.rolls && result.rolls.length > 0) {
			parts.push(`Rolls: [${result.rolls.join(', ')}]`);
		}

		// Show dropped dice
		if (result.dropped && result.dropped.length > 0) {
			parts.push(`Dropped: [${result.dropped.join(', ')}]`);
		}

		// Show rerolls
		if (result.rerolls && result.rerolls.length > 0) {
			const rerollText = result.rerolls.map(r => `${r.original}→${r.new}`).join(', ');
			parts.push(`Rerolled: ${rerollText}`);
		}

		// Show modifiers
		if (result.modifier && result.modifier !== 0) {
			parts.push(`Modifier: ${result.modifier > 0 ? '+' : ''}${result.modifier}`);
		}

		// Show character bonus
		if (result.character_bonus && result.character_bonus !== 0) {
			parts.push(`Character Bonus: ${result.character_bonus > 0 ? '+' : ''}${result.character_bonus}`);
		}

		return parts.join(' | ');
	};

	return (
		<div className={styles.diceRoller}>
			<div className={styles.diceRollerHeader}>
				<h3>Dice Roller</h3>
			</div>

			<div className={styles.diceInputSection}>
				<div className={styles.notationInput}>
					<label htmlFor="dice-notation">Dice Notation:</label>
					<input
						id="dice-notation"
						type="text"
						value={notation}
						onChange={(e) => setNotation(e.target.value)}
						placeholder="e.g., 1d20+5, 4d6dl1"
						disabled={isRolling}
					/>
				</div>

				{characterId && (
					<div className={styles.skillInput}>
						<label htmlFor="skill-select">Skill (optional):</label>
						<select
							id="skill-select"
							value={skill}
							onChange={(e) => setSkill(e.target.value)}
							disabled={isRolling}
						>
							<option value="">No skill</option>
							{skillOptions.map(skillOption => (
								<option key={skillOption} value={skillOption}>
									{skillOption.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
								</option>
							))}
						</select>
					</div>
				)}

				<button
					className={styles.rollButton}
					onClick={() => rollDice()}
					disabled={isRolling || !notation.trim()}
				>
					{isRolling ? 'Rolling...' : 'Roll Dice'}
				</button>
			</div>

			<div className={styles.commonRolls}>
				<h4>Quick Rolls:</h4>
				<div className={styles.quickRollButtons}>
					{commonRolls.map((roll) => (
						<button
							key={roll.notation}
							className={styles.quickRollButton}
							onClick={() => rollDice(roll.notation)}
							disabled={isRolling}
						>
							{roll.label}
						</button>
					))}
				</div>
			</div>

			{lastResult && (
				<div className={styles.lastResult}>
					<h4>Last Roll:</h4>
					<div className={styles.resultDisplay}>
						<div className={styles.resultNotation}>{lastResult.notation}</div>
						<div className={styles.resultTotal}>Total: {lastResult.total}</div>
						<div className={styles.resultDetails}>{formatResult(lastResult)}</div>
					</div>
				</div>
			)}

			{rollHistory.length > 0 && (
				<div className={styles.rollHistory}>
					<h4>Recent Rolls:</h4>
					<div className={styles.historyList}>
						{rollHistory.map((result, index) => (
							<div key={`${result.timestamp}-${index}`} className={styles.historyItem}>
								<span className={styles.historyNotation}>{result.notation}</span>
								<span className={styles.historyTotal}>{result.total}</span>
								<span className={styles.historyTime}>
									{new Date(result.timestamp).toLocaleTimeString()}
								</span>
							</div>
						))}
					</div>
				</div>
			)}
		</div>
	);
};

export default DiceRoller;