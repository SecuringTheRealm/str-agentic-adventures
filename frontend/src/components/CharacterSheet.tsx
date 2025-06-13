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

	// Helper function to get the primary spellcasting ability for a class
	const getSpellcastingAbility = (characterClass: string): keyof typeof character.abilities | null => {
		const spellcastingClasses = {
			wizard: 'intelligence',
			artificer: 'intelligence',
			cleric: 'wisdom',
			druid: 'wisdom',
			ranger: 'wisdom',
			bard: 'charisma',
			paladin: 'charisma',
			sorcerer: 'charisma',
			warlock: 'charisma'
		} as const;

		const className = characterClass.toLowerCase() as keyof typeof spellcastingClasses;
		return spellcastingClasses[className] || null;
	};

	// Helper function to calculate spell attack bonus
	const getSpellAttackBonus = (): string | null => {
		const spellcastingAbility = getSpellcastingAbility(character.character_class);
		if (!spellcastingAbility) return null;

		const abilityModifier = Math.floor((character.abilities[spellcastingAbility] - 10) / 2);
		const proficiencyBonus = Math.ceil(character.level / 4) + 1; // D&D 5e proficiency bonus formula
		const spellAttackBonus = abilityModifier + proficiencyBonus;
		
		return spellAttackBonus >= 0 ? `+${spellAttackBonus}` : spellAttackBonus.toString();
	};

	// Helper function to calculate spell save DC
	const getSpellSaveDC = (): number | null => {
		const spellcastingAbility = getSpellcastingAbility(character.character_class);
		if (!spellcastingAbility) return null;

		const abilityModifier = Math.floor((character.abilities[spellcastingAbility] - 10) / 2);
		const proficiencyBonus = Math.ceil(character.level / 4) + 1;
		
		return 8 + abilityModifier + proficiencyBonus;
	};

	// Filter cantrips (level 0 spells) from the character's spells
	const cantrips = character.spells?.filter(spell => spell.level === 0) || [];

	// Check if character is a spellcasting class
	const isSpellcaster = getSpellcastingAbility(character.character_class) !== null;

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

			{/* Spell Management Section for Spellcasting Classes */}
			{isSpellcaster && (
				<div className="spells">
					<h3>Spellcasting</h3>
					
					{/* Spell Attack Bonus and Save DC */}
					<div className="spell-stats">
						<div className="spell-attack">
							<div className="stat-label">Spell Attack</div>
							<div className="stat-value">{getSpellAttackBonus()}</div>
						</div>
						<div className="spell-save-dc">
							<div className="stat-label">Spell Save DC</div>
							<div className="stat-value">{getSpellSaveDC()}</div>
						</div>
					</div>

					{/* Cantrips */}
					<div className="cantrips">
						<h4>Cantrips</h4>
						<ul className="cantrips-list">
							{cantrips.length > 0 ? (
								cantrips.map((cantrip) => (
									<li key={cantrip.id} className="cantrip-item">
										<span className="cantrip-name">{cantrip.name}</span>
										<span className="cantrip-school">({cantrip.school})</span>
									</li>
								))
							) : (
								<li className="empty-cantrips">No cantrips known</li>
							)}
						</ul>
					</div>
				</div>
			)}
		</div>
	);
};

export default CharacterSheet;
