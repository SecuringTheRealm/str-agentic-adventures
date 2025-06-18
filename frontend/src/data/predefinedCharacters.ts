import type { Character } from '../services/api';

// Predefined characters following D&D 5e rules for quick selection
export const predefinedCharacters: Omit<Character, 'id'>[] = [
  {
    name: "Thorin Ironforge",
    race: "dwarf",
    character_class: "fighter",
    level: 1,
    abilities: {
      strength: 16,
      dexterity: 12,
      constitution: 15,
      intelligence: 10,
      wisdom: 13,
      charisma: 8
    },
    hit_points: {
      current: 11,
      maximum: 11
    },
    inventory: [
      { item_id: "Chain Mail", quantity: 1 },
      { item_id: "Battleaxe", quantity: 1 },
      { item_id: "Handaxe", quantity: 2 },
      { item_id: "Explorer's Pack", quantity: 1 }
    ]
  },
  {
    name: "Lyralei Swiftarrow",
    race: "elf",
    character_class: "ranger",
    level: 1,
    abilities: {
      strength: 13,
      dexterity: 16,
      constitution: 14,
      intelligence: 12,
      wisdom: 15,
      charisma: 10
    },
    hit_points: {
      current: 12,
      maximum: 12
    },
    inventory: [
      { item_id: "Studded Leather Armor", quantity: 1 },
      { item_id: "Longbow", quantity: 1 },
      { item_id: "Arrows", quantity: 20 },
      { item_id: "Shortsword", quantity: 1 },
      { item_id: "Dungeoneer's Pack", quantity: 1 }
    ]
  },
  {
    name: "Zara Moonwhisper",
    race: "human",
    character_class: "wizard",
    level: 1,
    abilities: {
      strength: 8,
      dexterity: 14,
      constitution: 13,
      intelligence: 16,
      wisdom: 12,
      charisma: 10
    },
    hit_points: {
      current: 7,
      maximum: 7
    },
    inventory: [
      { item_id: "Spellbook", quantity: 1 },
      { item_id: "Dagger", quantity: 1 },
      { item_id: "Component Pouch", quantity: 1 },
      { item_id: "Scholar's Pack", quantity: 1 }
    ]
  },
  {
    name: "Brother Marcus",
    race: "human",
    character_class: "cleric",
    level: 1,
    abilities: {
      strength: 14,
      dexterity: 10,
      constitution: 15,
      intelligence: 12,
      wisdom: 16,
      charisma: 13
    },
    hit_points: {
      current: 9,
      maximum: 9
    },
    inventory: [
      { item_id: "Chain Mail", quantity: 1 },
      { item_id: "Shield", quantity: 1 },
      { item_id: "Mace", quantity: 1 },
      { item_id: "Priest's Pack", quantity: 1 },
      { item_id: "Holy Symbol", quantity: 1 }
    ]
  },
  {
    name: "Shadowstep",
    race: "halfling",
    character_class: "rogue",
    level: 1,
    abilities: {
      strength: 10,
      dexterity: 16,
      constitution: 14,
      intelligence: 13,
      wisdom: 12,
      charisma: 15
    },
    hit_points: {
      current: 10,
      maximum: 10
    },
    inventory: [
      { item_id: "Leather Armor", quantity: 1 },
      { item_id: "Shortsword", quantity: 1 },
      { item_id: "Dagger", quantity: 2 },
      { item_id: "Thieves' Tools", quantity: 1 },
      { item_id: "Burglar's Pack", quantity: 1 }
    ]
  },
  {
    name: "Seraphina Brightflame",
    race: "dragonborn",
    character_class: "paladin",
    level: 1,
    abilities: {
      strength: 16,
      dexterity: 10,
      constitution: 14,
      intelligence: 12,
      wisdom: 13,
      charisma: 15
    },
    hit_points: {
      current: 12,
      maximum: 12
    },
    inventory: [
      { item_id: "Chain Mail", quantity: 1 },
      { item_id: "Shield", quantity: 1 },
      { item_id: "Longsword", quantity: 1 },
      { item_id: "Javelin", quantity: 5 },
      { item_id: "Explorer's Pack", quantity: 1 }
    ]
  }
];