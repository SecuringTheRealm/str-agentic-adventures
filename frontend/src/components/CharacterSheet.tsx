import type React from "react";
import { useMemo } from "react";
import type { Character } from "../services/api";
import styles from "./CharacterSheet.module.css";

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
  const calculateTotalWeight = useMemo(() => {
    return (inventory: any[]): number => {
      return inventory.reduce((total, item) => {
        const weight = (item as any).weight || 0;
        const quantity = item.quantity || 1;
        return total + weight * quantity;
      }, 0);
    };
  }, []);

  const getEncumbranceStatus = (character: Character): string => {
    const totalWeight = calculateTotalWeight(character.inventory || []);
    const strength = character.abilities.strength;
    const carryingCapacity = (strength || 10) * 15;
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
    const spellcasterClasses = [
      "wizard",
      "sorcerer",
      "cleric",
      "druid",
      "bard",
      "warlock",
      "paladin",
      "ranger",
    ];
    return spellcasterClasses.includes(characterClass.toLowerCase());
  };

  const getSpellcastingAbility = (characterClass: string): string => {
    const spellcastingAbilities: { [key: string]: string } = {
      wizard: "Intelligence",
      sorcerer: "Charisma",
      cleric: "Wisdom",
      druid: "Wisdom",
      bard: "Charisma",
      warlock: "Charisma",
      paladin: "Charisma",
      ranger: "Wisdom",
    };
    return spellcastingAbilities[characterClass.toLowerCase()] || "None";
  };

  const calculateSpellSaveDC = (character: Character): number => {
    const proficiencyBonus = Math.ceil((character.level || 1) / 4) + 1;
    const spellcastingAbility = getSpellcastingAbility(
      character.character_class || "fighter"
    );
    let abilityModifier = 0;

    switch (spellcastingAbility) {
      case "Intelligence":
        abilityModifier = Math.floor(
          ((character.abilities.intelligence || 10) - 10) / 2
        );
        break;
      case "Wisdom":
        abilityModifier = Math.floor(
          ((character.abilities.wisdom || 10) - 10) / 2
        );
        break;
      case "Charisma":
        abilityModifier = Math.floor(
          ((character.abilities.charisma || 10) - 10) / 2
        );
        break;
    }

    return 8 + proficiencyBonus + abilityModifier;
  };

  const calculateSpellAttackBonus = (character: Character): number => {
    const proficiencyBonus = Math.ceil((character.level || 1) / 4) + 1;
    const spellcastingAbility = getSpellcastingAbility(
      character.character_class || "fighter"
    );
    let abilityModifier = 0;

    switch (spellcastingAbility) {
      case "Intelligence":
        abilityModifier = Math.floor(
          ((character.abilities.intelligence || 10) - 10) / 2
        );
        break;
      case "Wisdom":
        abilityModifier = Math.floor(
          ((character.abilities.wisdom || 10) - 10) / 2
        );
        break;
      case "Charisma":
        abilityModifier = Math.floor(
          ((character.abilities.charisma || 10) - 10) / 2
        );
        break;
    }

    return proficiencyBonus + abilityModifier;
  };

  const getMaxSpellSlots = (character: Character, level: number): number => {
    // Simplified spell slot calculation based on character level and class
    if (!isSpellcaster(character.character_class || "fighter")) return 0;

    const characterLevel = character.level || 1;
    const classType = (character.character_class || "fighter").toLowerCase();

    // Warlock uses different spell slot progression
    if (classType === "warlock") {
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
    if (classType === "paladin" || classType === "ranger") {
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
    <div className={styles.characterSheet}>
      <div className={styles.characterHeader}>
        <h2>{character.name}</h2>
        <div className={styles.characterBasics}>
          <div>
            Level {character.level} {character.race} {character.character_class}
          </div>
        </div>
      </div>

      <div className={styles.characterStats}>
        <div className={styles.hitPoints}>
          <div className={styles.statLabel}>Hit Points</div>
          <div className={styles.statValue}>
            {character.hit_points.current} / {character.hit_points.maximum}
          </div>
        </div>

        <div className={styles.armorClass}>
          <div className={styles.statLabel}>Armor Class</div>
          <div className={styles.statValue}>10</div>{" "}
          {/* Would be calculated from equipment and stats */}
        </div>
      </div>

      <div className={styles.abilities}>
        <h3>Abilities</h3>
        <div className={styles.abilitiesGrid}>
          <div className={styles.ability}>
            <div className={styles.abilityName}>STR</div>
            <div className={styles.abilityScore}>
              {character.abilities.strength || 10}
            </div>
            <div className={styles.abilityMod}>
              {getAbilityModifier(character.abilities.strength || 10)}
            </div>
          </div>
          <div className={styles.ability}>
            <div className={styles.abilityName}>DEX</div>
            <div className={styles.abilityScore}>
              {character.abilities.dexterity || 10}
            </div>
            <div className={styles.abilityMod}>
              {getAbilityModifier(character.abilities.dexterity || 10)}
            </div>
          </div>
          <div className={styles.ability}>
            <div className={styles.abilityName}>CON</div>
            <div className={styles.abilityScore}>
              {character.abilities.constitution || 10}
            </div>
            <div className={styles.abilityMod}>
              {getAbilityModifier(character.abilities.constitution || 10)}
            </div>
          </div>
          <div className={styles.ability}>
            <div className={styles.abilityName}>INT</div>
            <div className={styles.abilityScore}>
              {character.abilities.intelligence || 10}
            </div>
            <div className={styles.abilityMod}>
              {getAbilityModifier(character.abilities.intelligence || 10)}
            </div>
          </div>
          <div className={styles.ability}>
            <div className={styles.abilityName}>WIS</div>
            <div className={styles.abilityScore}>
              {character.abilities.wisdom || 10}
            </div>
            <div className={styles.abilityMod}>
              {getAbilityModifier(character.abilities.wisdom || 10)}
            </div>
          </div>
          <div className={styles.ability}>
            <div className={styles.abilityName}>CHA</div>
            <div className={styles.abilityScore}>
              {character.abilities.charisma || 10}
            </div>
            <div className={styles.abilityMod}>
              {getAbilityModifier(character.abilities.charisma || 10)}
            </div>
          </div>
        </div>
      </div>

      <div className={styles.inventory}>
        <h3>Inventory</h3>

        {/* Equipment Slots */}
        <div className={styles.equipmentSlots}>
          <h4>Equipment</h4>
          <div className={styles.equipmentGrid}>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Main Hand:</div>
              <span>
                {(character as any).equipment?.mainHand?.name || "Empty"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Off Hand:</div>
              <span>
                {(character as any).equipment?.offHand?.name || "Empty"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Armor:</div>
              <span>
                {(character as any).equipment?.armor?.name || "Unarmored"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Shield:</div>
              <span>
                {(character as any).equipment?.shield?.name || "None"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Ring 1:</div>
              <span>
                {(character as any).equipment?.ring1?.name || "Empty"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Ring 2:</div>
              <span>
                {(character as any).equipment?.ring2?.name || "Empty"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Amulet:</div>
              <span>
                {(character as any).equipment?.amulet?.name || "Empty"}
              </span>
            </div>
            <div className={styles.equipmentSlot}>
              <div className={styles.slotLabel}>Cloak:</div>
              <span>
                {(character as any).equipment?.cloak?.name || "Empty"}
              </span>
            </div>
          </div>
        </div>

        {/* Inventory Items */}
        <div className={styles.inventoryItems}>
          <h4>Items</h4>
          <div className={styles.inventoryHeader}>
            <span>
              Total Weight: {calculateTotalWeight(character.inventory || [])}{" "}
              lbs
            </span>
            <span className={getEncumbranceClass(character)}>
              Encumbrance: {getEncumbranceStatus(character)}
            </span>
          </div>
          <ul className={styles.inventoryList}>
            {character.inventory && character.inventory.length > 0 ? (
              character.inventory.map((item: any, index: number) => (
                <li
                  key={`${(item as any).name || item.item_id}-${index}`}
                  className={styles.inventoryItem}
                >
                  <span className={styles.itemName}>
                    {(item as any).name || item.item_id}
                  </span>
                  <span
                    className={`item-rarity rarity-${(item as any).rarity || "common"}`}
                  >
                    {getRarityDisplay((item as any).rarity)}
                  </span>
                  {item.quantity > 1 && (
                    <span className={styles.itemQuantity}>
                      x{item.quantity}
                    </span>
                  )}
                  <span className={styles.itemWeight}>
                    {(item as any).weight || 0} lbs
                  </span>
                  {(item as any).value && (
                    <span className={styles.itemValue}>
                      {(item as any).value} gp
                    </span>
                  )}
                  {(item as any).magical && (
                    <span className={styles.magicalIndicator}>✨</span>
                  )}
                </li>
              ))
            ) : (
              <li className={styles.emptyInventory}>No items in inventory</li>
            )}
          </ul>
        </div>
      </div>

      {/* Spell Management Section */}
      {isSpellcaster(character.character_class || "fighter") && (
        <div className={styles.spellManagement}>
          <h3>Spells</h3>

          {/* Spell Save DC and Attack Bonus */}
          <div className={styles.spellStats}>
            <div className={styles.spellStat}>
              <div className={styles.statLabel}>Spell Save DC:</div>
              <span>{calculateSpellSaveDC(character)}</span>
            </div>
            <div className={styles.spellStat}>
              <div className={styles.statLabel}>Spell Attack Bonus:</div>
              <span>+{calculateSpellAttackBonus(character)}</span>
            </div>
            <div className={styles.spellStat}>
              <div className={styles.statLabel}>Spellcasting Ability:</div>
              <span>
                {getSpellcastingAbility(character.character_class || "fighter")}
              </span>
            </div>
          </div>

          {/* Spell Slots */}
          <div className={styles.spellSlots}>
            <h4>Spell Slots</h4>
            <div className={styles.spellSlotGrid}>
              {Array.from({ length: 9 }, (_, level) => level + 1).map(
                (level) => {
                  const maxSlots = getMaxSpellSlots(character, level);
                  const usedSlots = (character as any).spellSlots?.[level] || 0;
                  if (maxSlots === 0) return null;

                  return (
                    <div key={level} className={styles.spellSlotLevel}>
                      <div className={styles.levelLabel}>Level {level}:</div>
                      <div className={styles.slotIndicators}>
                        {Array.from({ length: maxSlots }, (_, i) => (
                          <div
                            key={i}
                            className={`slot-indicator ${i < usedSlots ? "used" : "available"}`}
                          >
                            ○
                          </div>
                        ))}
                        <span className={styles.slotCount}>
                          ({usedSlots}/{maxSlots})
                        </span>
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </div>

          {/* Cantrips */}
          <div className={styles.cantrips}>
            <h4>Cantrips</h4>
            <ul className={styles.spellList}>
              {(character as any).spells?.cantrips?.map(
                (spell: any, index: number) => (
                  <li key={index} className="spell-item cantrip">
                    <span className={styles.spellName}>{spell.name}</span>
                    <span className={styles.spellSchool}>{spell.school}</span>
                    <button type="button" className={styles.castButton}>
                      Cast
                    </button>
                  </li>
                )
              ) || <li>No cantrips known</li>}
            </ul>
          </div>

          {/* Prepared Spells */}
          <div className={styles.preparedSpells}>
            <h4>Prepared Spells</h4>
            {Array.from({ length: 9 }, (_, level) => level + 1).map((level) => {
              const levelSpells =
                (character as any).spells?.prepared?.filter(
                  (spell: any) => spell.level === level
                ) || [];
              if (levelSpells.length === 0) return null;

              return (
                <div key={level} className={styles.spellLevelGroup}>
                  <h5>Level {level} Spells</h5>
                  <ul className={styles.spellList}>
                    {levelSpells.map((spell: any, index: number) => (
                      <li key={index} className={styles.spellItem}>
                        <span className={styles.spellName}>{spell.name}</span>
                        <span className={styles.spellSchool}>
                          {spell.school}
                        </span>
                        <span className={styles.spellCastingTime}>
                          {spell.castingTime}
                        </span>
                        <span className={styles.spellRange}>{spell.range}</span>
                        {spell.concentration && (
                          <span className={styles.concentrationIndicator}>
                            C
                          </span>
                        )}
                        {spell.ritual && (
                          <span className={styles.ritualIndicator}>R</span>
                        )}
                        <button
                          type="button"
                          className={styles.castButton}
                          disabled={!hasSpellSlot(character, level)}
                        >
                          Cast
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
            {!(character as any).spells?.prepared?.length && (
              <p>No spells prepared</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CharacterSheet;
