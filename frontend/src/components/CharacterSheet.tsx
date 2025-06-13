import type React from "react";
import type { Character } from "../services/api";
import "./CharacterSheet.css";

interface CharacterSheetProps {
	character: Character;
}

const CharacterSheet: React.FC<CharacterSheetProps> = ({ character }) => {
	// Helper function to calculate ability modifier
	const getAbilityModifier = (score: number): string => {
		const modifier = Math.floor((score - 10) / 2);
		return modifier >= 0 ? `+${modifier}` : modifier.toString();
	};

	// Helper function to calculate carrying capacity
	const getCarryingCapacity = (strengthScore: number): number => {
		return strengthScore * 15; // D&D 5e rule: Strength × 15 pounds
	};

	// Helper function to calculate total inventory weight
	const getTotalInventoryWeight = (): number => {
		if (!character.inventory) return 0;
		return character.inventory.reduce((total, item) => {
			const itemWeight = item.weight || 0;
			return total + (itemWeight * item.quantity);
		}, 0);
	};

	// Helper function to get encumbrance status
	const getEncumbranceStatus = (totalWeight: number, capacity: number): { status: string; color: string } => {
		if (totalWeight > capacity) {
			return { status: "Heavily Encumbered", color: "#dc3545" }; // Red
		} else if (totalWeight > capacity - 5) {
			return { status: "Encumbered", color: "#ffc107" }; // Yellow
		}
		return { status: "Normal", color: "#28a745" }; // Green
	};

	const carryingCapacity = getCarryingCapacity(character.abilities.strength);
	const totalWeight = getTotalInventoryWeight();
	const encumbrance = getEncumbranceStatus(totalWeight, carryingCapacity);

	return (
		<div className="character-sheet">
			<div className="character-header">
				<h2>{character.name}</h2>
				<div className="character-basics">
					<div>
						Level {character.level} {character.race} {character.character_class}
					</div>
				</div>
			</div>

			<div className="character-stats">
				<div className="hit-points">
					<div className="stat-label">Hit Points</div>
					<div className="stat-value">
						{character.hit_points.current} / {character.hit_points.maximum}
					</div>
				</div>

				<div className="armor-class">
					<div className="stat-label">Armor Class</div>
					<div className="stat-value">10</div>{" "}
					{/* Would be calculated from equipment and stats */}
				</div>
			</div>

			<div className="abilities">
				<h3>Abilities</h3>
				<div className="abilities-grid">
					<div className="ability">
						<div className="ability-name">STR</div>
						<div className="ability-score">{character.abilities.strength}</div>
						<div className="ability-mod">
							{getAbilityModifier(character.abilities.strength)}
						</div>
					</div>
					<div className="ability">
						<div className="ability-name">DEX</div>
						<div className="ability-score">{character.abilities.dexterity}</div>
						<div className="ability-mod">
							{getAbilityModifier(character.abilities.dexterity)}
						</div>
					</div>
					<div className="ability">
						<div className="ability-name">CON</div>
						<div className="ability-score">
							{character.abilities.constitution}
						</div>
						<div className="ability-mod">
							{getAbilityModifier(character.abilities.constitution)}
						</div>
					</div>
					<div className="ability">
						<div className="ability-name">INT</div>
						<div className="ability-score">
							{character.abilities.intelligence}
						</div>
						<div className="ability-mod">
							{getAbilityModifier(character.abilities.intelligence)}
						</div>
					</div>
					<div className="ability">
						<div className="ability-name">WIS</div>
						<div className="ability-score">{character.abilities.wisdom}</div>
						<div className="ability-mod">
							{getAbilityModifier(character.abilities.wisdom)}
						</div>
					</div>
					<div className="ability">
						<div className="ability-name">CHA</div>
						<div className="ability-score">{character.abilities.charisma}</div>
						<div className="ability-mod">
							{getAbilityModifier(character.abilities.charisma)}
						</div>
					</div>
				</div>
			</div>

			<div className="inventory">
				<h3>Inventory</h3>
				{/* TODO: Add equipment slot management (armor, weapons, rings, etc.) */}
				{/* TODO: Add magical item effects display and stat modifications */}
				{/* TODO: Add item rarity indicators and value displays */}
				
				{/* Encumbrance Information */}
				<div className="encumbrance-info">
					<div className="encumbrance-summary">
						<span className="weight-display">
							Total Weight: {totalWeight.toFixed(1)} / {carryingCapacity} lbs
						</span>
						<span 
							className="encumbrance-status" 
							style={{ color: encumbrance.color }}
						>
							{encumbrance.status}
						</span>
					</div>
					<div className="weight-bar">
						<div 
							className="weight-progress" 
							style={{ 
								width: `${Math.min((totalWeight / carryingCapacity) * 100, 100)}%`,
								backgroundColor: encumbrance.color
							}}
						/>
					</div>
				</div>

				<ul className="inventory-list">
					{character.inventory && character.inventory.length > 0 ? (
						character.inventory.map((item, index) => (
							<li key={`${item.name}-${index}`} className="inventory-item">
								<span className="item-name">{item.name}</span>
								<div className="item-details">
									{item.quantity > 1 && (
										<span className="item-quantity">x{item.quantity}</span>
									)}
									{item.weight && (
										<span className="item-weight">
											{(item.weight * item.quantity).toFixed(1)} lbs
										</span>
									)}
								</div>
							</li>
						))
					) : (
						<li className="empty-inventory">No items in inventory</li>
					)}
				</ul>
			</div>

			{/* TODO: Add spell management section for spellcasting classes */}
			{/* TODO: Include spell slot tracking and spell save DC display */}
			{/* TODO: Add prepared spells list with casting options */}
			{/* TODO: Add cantrip management and spell attack bonus display */}
		</div>
	);
};

export default CharacterSheet;
