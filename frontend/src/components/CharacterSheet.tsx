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

	return (
		<div className="character-sheet">
			<div className="character-header">
				<h2>{character.name}</h2>
				<div className="character-basics">
					<div>
						Level {character.level} {character.race} {character.class}
					</div>
				</div>
			</div>

			<div className="character-stats">
				<div className="hit-points">
					<div className="stat-label">Hit Points</div>
					<div className="stat-value">
						{character.hitPoints.current} / {character.hitPoints.maximum}
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
				<ul className="inventory-list">
					{character.inventory && character.inventory.length > 0 ? (
						character.inventory.map((item, index) => (
							<li key={`${item.name}-${index}`} className="inventory-item">
								<span className="item-name">{item.name}</span>
								{item.quantity > 1 && (
									<span className="item-quantity">x{item.quantity}</span>
								)}
							</li>
						))
					) : (
						<li className="empty-inventory">No items in inventory</li>
					)}
				</ul>
			</div>
		</div>
	);
};

export default CharacterSheet;
