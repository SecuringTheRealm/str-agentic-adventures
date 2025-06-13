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

	// Helper functions for inventory and equipment management
	const calculateTotalWeight = (inventory: any[]): number => {
		return inventory.reduce((total, item) => {
			const weight = (item as any).weight || 0;
			const quantity = item.quantity || 1;
			return total + (weight * quantity);
		}, 0);
	};

	const getEncumbranceStatus = (character: Character): string => {
		const totalWeight = calculateTotalWeight(character.inventory || []);
		const strength = character.abilities.strength;
		const carryingCapacity = strength * 15;
		const heavyLoad = carryingCapacity * 2;
		
		if (totalWeight <= carryingCapacity) return "Normal";
		if (totalWeight <= heavyLoad) return "Encumbered";
		return "Heavily Encumbered";
	};

	const getEncumbranceClass = (character: Character): string => {
		const status = getEncumbranceStatus(character);
		return `encumbrance ${status.toLowerCase().replace(" ", "-")}`;
	};

	const getRarityDisplay = (rarity?: string): string => {
		if (!rarity) return "Common";
		return rarity.charAt(0).toUpperCase() + rarity.slice(1);
	};

	// Helper functions for spell management
	const isSpellcaster = (characterClass: string): boolean => {
		const spellcasterClasses = ['wizard', 'sorcerer', 'cleric', 'druid', 'bard', 'warlock', 'paladin', 'ranger'];
		return spellcasterClasses.includes(characterClass.toLowerCase());
	};

	const getSpellcastingAbility = (characterClass: string): string => {
		const spellcastingAbilities: { [key: string]: string } = {
			'wizard': 'Intelligence',
			'sorcerer': 'Charisma',
			'cleric': 'Wisdom',
			'druid': 'Wisdom',
			'bard': 'Charisma',
			'warlock': 'Charisma',
			'paladin': 'Charisma',
			'ranger': 'Wisdom'
		};
		return spellcastingAbilities[characterClass.toLowerCase()] || 'None';
	};

	const calculateSpellSaveDC = (character: Character): number => {
		const proficiencyBonus = Math.ceil(character.level / 4) + 1;
		const spellcastingAbility = getSpellcastingAbility(character.character_class);
		let abilityModifier = 0;
		
		switch (spellcastingAbility) {
			case 'Intelligence':
				abilityModifier = Math.floor((character.abilities.intelligence - 10) / 2);
				break;
			case 'Wisdom':
				abilityModifier = Math.floor((character.abilities.wisdom - 10) / 2);
				break;
			case 'Charisma':
				abilityModifier = Math.floor((character.abilities.charisma - 10) / 2);
				break;
		}
		
		return 8 + proficiencyBonus + abilityModifier;
	};

	const calculateSpellAttackBonus = (character: Character): number => {
		const proficiencyBonus = Math.ceil(character.level / 4) + 1;
		const spellcastingAbility = getSpellcastingAbility(character.character_class);
		let abilityModifier = 0;
		
		switch (spellcastingAbility) {
			case 'Intelligence':
				abilityModifier = Math.floor((character.abilities.intelligence - 10) / 2);
				break;
			case 'Wisdom':
				abilityModifier = Math.floor((character.abilities.wisdom - 10) / 2);
				break;
			case 'Charisma':
				abilityModifier = Math.floor((character.abilities.charisma - 10) / 2);
				break;
		}
		
		return proficiencyBonus + abilityModifier;
	};

	const getMaxSpellSlots = (character: Character, level: number): number => {
		// Simplified spell slot calculation based on character level and class
		if (!isSpellcaster(character.character_class)) return 0;
		
		const characterLevel = character.level;
		const classType = character.character_class.toLowerCase();
		
		// Warlock uses different spell slot progression
		if (classType === 'warlock') {
			if (level > 5) return 0;
			if (characterLevel >= 17) return level <= 5 ? 4 : 0;
			if (characterLevel >= 11) return level <= 4 ? 3 : 0;
			if (characterLevel >= 7) return level <= 3 ? 2 : 0;
			if (characterLevel >= 3) return level <= 2 ? 2 : 0;
			return level === 1 ? 1 : 0;
		}
		
		// Standard spell slot progression for full casters
		const spellSlotTable: { [level: number]: number[] } = {
			1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
			2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
			3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
			4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
			5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
			6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
			7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
			8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
			9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
			10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
			11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
			12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
			13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
			14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
			15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
			16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
			17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
			18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
			19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
			20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
		};
		
		// Half-casters (Paladin, Ranger) get spells later and fewer slots
		if (classType === 'paladin' || classType === 'ranger') {
			if (characterLevel < 2) return 0;
			const halfCasterLevel = Math.floor(characterLevel / 2);
			const slots = spellSlotTable[halfCasterLevel];
			return slots ? slots[level - 1] : 0;
		}
		
		const slots = spellSlotTable[characterLevel];
		return slots ? slots[level - 1] : 0;
	};

	const hasSpellSlot = (character: Character, level: number): boolean => {
		const maxSlots = getMaxSpellSlots(character, level);
		const usedSlots = (character as any).spellSlots?.[level] || 0;
		return usedSlots < maxSlots;
	};

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
				
				{/* Equipment Slots */}
				<div className="equipment-slots">
					<h4>Equipment</h4>
					<div className="equipment-grid">
						<div className="equipment-slot">
							<label>Main Hand:</label>
							<span>{(character as any).equipment?.mainHand?.name || "Empty"}</span>
						</div>
						<div className="equipment-slot">
							<label>Off Hand:</label>
							<span>{(character as any).equipment?.offHand?.name || "Empty"}</span>
						</div>
						<div className="equipment-slot">
							<label>Armor:</label>
							<span>{(character as any).equipment?.armor?.name || "Unarmored"}</span>
						</div>
						<div className="equipment-slot">
							<label>Shield:</label>
							<span>{(character as any).equipment?.shield?.name || "None"}</span>
						</div>
						<div className="equipment-slot">
							<label>Ring 1:</label>
							<span>{(character as any).equipment?.ring1?.name || "Empty"}</span>
						</div>
						<div className="equipment-slot">
							<label>Ring 2:</label>
							<span>{(character as any).equipment?.ring2?.name || "Empty"}</span>
						</div>
						<div className="equipment-slot">
							<label>Amulet:</label>
							<span>{(character as any).equipment?.amulet?.name || "Empty"}</span>
						</div>
						<div className="equipment-slot">
							<label>Cloak:</label>
							<span>{(character as any).equipment?.cloak?.name || "Empty"}</span>
						</div>
					</div>
				</div>

				{/* Inventory Items */}
				<div className="inventory-items">
					<h4>Items</h4>
					<div className="inventory-header">
						<span>Total Weight: {calculateTotalWeight(character.inventory || [])} lbs</span>
						<span className={getEncumbranceClass(character)}>
							Encumbrance: {getEncumbranceStatus(character)}
						</span>
					</div>
					<ul className="inventory-list">
						{character.inventory && character.inventory.length > 0 ? (
							character.inventory.map((item, index) => (
								<li key={`${item.name}-${index}`} className="inventory-item">
									<span className="item-name">{item.name}</span>
									<span className={`item-rarity rarity-${(item as any).rarity || 'common'}`}>
										{getRarityDisplay((item as any).rarity)}
									</span>
									{item.quantity > 1 && (
										<span className="item-quantity">x{item.quantity}</span>
									)}
									<span className="item-weight">{(item as any).weight || 0} lbs</span>
									{(item as any).value && (
										<span className="item-value">{(item as any).value} gp</span>
									)}
									{(item as any).magical && (
										<span className="magical-indicator">✨</span>
									)}
								</li>
							))
						) : (
							<li className="empty-inventory">No items in inventory</li>
						)}
					</ul>
				</div>
			</div>

			{/* Spell Management Section */}
			{isSpellcaster(character.character_class) && (
				<div className="spell-management">
					<h3>Spells</h3>
					
					{/* Spell Save DC and Attack Bonus */}
					<div className="spell-stats">
						<div className="spell-stat">
							<label>Spell Save DC:</label>
							<span>{calculateSpellSaveDC(character)}</span>
						</div>
						<div className="spell-stat">
							<label>Spell Attack Bonus:</label>
							<span>+{calculateSpellAttackBonus(character)}</span>
						</div>
						<div className="spell-stat">
							<label>Spellcasting Ability:</label>
							<span>{getSpellcastingAbility(character.character_class)}</span>
						</div>
					</div>

					{/* Spell Slots */}
					<div className="spell-slots">
						<h4>Spell Slots</h4>
						<div className="spell-slot-grid">
							{Array.from({ length: 9 }, (_, level) => level + 1).map(level => {
								const maxSlots = getMaxSpellSlots(character, level);
								const usedSlots = (character as any).spellSlots?.[level] || 0;
								if (maxSlots === 0) return null;
								
								return (
									<div key={level} className="spell-slot-level">
										<label>Level {level}:</label>
										<div className="slot-indicators">
											{Array.from({ length: maxSlots }, (_, i) => (
												<div 
													key={i} 
													className={`slot-indicator ${i < usedSlots ? 'used' : 'available'}`}
												>
													○
												</div>
											))}
											<span className="slot-count">({usedSlots}/{maxSlots})</span>
										</div>
									</div>
								);
							})}
						</div>
					</div>

					{/* Cantrips */}
					<div className="cantrips">
						<h4>Cantrips</h4>
						<ul className="spell-list">
							{(character as any).spells?.cantrips?.map((spell: any, index: number) => (
								<li key={index} className="spell-item cantrip">
									<span className="spell-name">{spell.name}</span>
									<span className="spell-school">{spell.school}</span>
									<button className="cast-button">Cast</button>
								</li>
							)) || <li>No cantrips known</li>}
						</ul>
					</div>

					{/* Prepared Spells */}
					<div className="prepared-spells">
						<h4>Prepared Spells</h4>
						{Array.from({ length: 9 }, (_, level) => level + 1).map(level => {
							const levelSpells = (character as any).spells?.prepared?.filter((spell: any) => spell.level === level) || [];
							if (levelSpells.length === 0) return null;
							
							return (
								<div key={level} className="spell-level-group">
									<h5>Level {level} Spells</h5>
									<ul className="spell-list">
										{levelSpells.map((spell: any, index: number) => (
											<li key={index} className="spell-item">
												<span className="spell-name">{spell.name}</span>
												<span className="spell-school">{spell.school}</span>
												<span className="spell-casting-time">{spell.castingTime}</span>
												<span className="spell-range">{spell.range}</span>
												{spell.concentration && <span className="concentration-indicator">C</span>}
												{spell.ritual && <span className="ritual-indicator">R</span>}
												<button className="cast-button" disabled={!hasSpellSlot(character, level)}>
													Cast
												</button>
											</li>
										))}
									</ul>
								</div>
							);
						})}
						{!(character as any).spells?.prepared?.length && <p>No spells prepared</p>}
					</div>
				</div>
			)}
		</div>
	);
};

export default CharacterSheet;
