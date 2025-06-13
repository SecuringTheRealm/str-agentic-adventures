import type React from "react";
import type { Character, Spell } from "../services/api";
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

	// Helper function to check if character class can cast spells
	const isSpellcaster = (characterClass: string): boolean => {
		const spellcastingClasses = ['wizard', 'cleric', 'bard', 'druid', 'warlock', 'sorcerer', 'paladin', 'ranger'];
		return spellcastingClasses.includes(characterClass.toLowerCase());
	};

	// Helper function to get spellcasting ability modifier
	const getSpellcastingModifier = (characterClass: string): number => {
		const classAbilityMap: { [key: string]: keyof typeof character.abilities } = {
			'wizard': 'intelligence',
			'warlock': 'charisma',
			'sorcerer': 'charisma',
			'bard': 'charisma',
			'cleric': 'wisdom',
			'druid': 'wisdom',
			'paladin': 'charisma',
			'ranger': 'wisdom'
		};
		const ability = classAbilityMap[characterClass.toLowerCase()];
		return ability ? Math.floor((character.abilities[ability] - 10) / 2) : 0;
	};

	// Calculate spell save DC and attack bonus
	const proficiencyBonus = character.proficiency_bonus ?? Math.ceil(character.level / 4) + 1; // Default calculation
	const spellcastingModifier = getSpellcastingModifier(character.character_class);
	const spellSaveDC = 8 + proficiencyBonus + spellcastingModifier;
	const spellAttackBonus = proficiencyBonus + spellcastingModifier;

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
				{/* TODO: Add item weight tracking and encumbrance calculations */}
				{/* TODO: Add magical item effects display and stat modifications */}
				{/* TODO: Add item rarity indicators and value displays */}
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

			{/* Spell Management Section for spellcasting classes */}
			{isSpellcaster(character.character_class) && (
				<div className="spells">
					<h3>Spells</h3>
					
					{/* Spell save DC and attack bonus */}
					<div className="spell-stats">
						<div className="spell-stat">
							<div className="stat-label">Spell Save DC</div>
							<div className="stat-value">{spellSaveDC}</div>
						</div>
						<div className="spell-stat">
							<div className="stat-label">Spell Attack Bonus</div>
							<div className="stat-value">{spellAttackBonus >= 0 ? `+${spellAttackBonus}` : spellAttackBonus}</div>
						</div>
					</div>

					{/* Prepared spells list */}
					<div className="prepared-spells">
						<h4>Prepared Spells</h4>
						{character.spells && character.spells.length > 0 ? (
							<div className="spells-by-level">
								{/* Group spells by level */}
								{[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
									.filter(level => character.spells?.some(spell => spell.level === level))
									.map(level => (
										<div key={level} className="spell-level-group">
											<h5 className="spell-level-header">
												{level === 0 ? 'Cantrips' : `Level ${level}`}
											</h5>
											<ul className="spell-list">
												{character.spells
													?.filter(spell => spell.level === level)
													.map((spell, index) => (
														<li key={`${spell.id}-${index}`} className="spell-item">
															<div className="spell-info">
																<span className="spell-name">{spell.name}</span>
																<span className="spell-school">{spell.school}</span>
															</div>
															<div className="spell-details">
																<span className="spell-casting-time">{spell.casting_time}</span>
																<span className="spell-range">{spell.range}</span>
															</div>
															<div className="spell-actions">
																<button 
																	className="cast-spell-btn"
																	title={`Cast ${spell.name}`}
																	onClick={() => {
																		// TODO: Implement spell casting logic
																		console.log(`Casting ${spell.name}`);
																	}}
																>
																	Cast
																</button>
															</div>
														</li>
													))}
											</ul>
										</div>
									))}
							</div>
						) : (
							<div className="no-spells">No spells prepared</div>
						)}
					</div>
				</div>
			)}
		</div>
	);
};

export default CharacterSheet;
