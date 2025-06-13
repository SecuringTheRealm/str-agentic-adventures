import type { Character } from '../services/api';

// Predefined characters following D&D 5e rules for quick selection
export const predefinedCharacters: Omit<Character, 'id'>[] = [
  {
    name: "Thorin Ironforge",
    race: "Dwarf",
    character_class: "Fighter",
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
      { name: "Chain Mail", quantity: 1 },
      { name: "Battleaxe", quantity: 1 },
      { name: "Handaxe", quantity: 2 },
      { name: "Explorer's Pack", quantity: 1 }
    ]
  },
  {
    name: "Lyralei Swiftarrow",
    race: "Elf",
    character_class: "Ranger",
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
      { name: "Studded Leather Armor", quantity: 1 },
      { name: "Longbow", quantity: 1 },
      { name: "Arrows", quantity: 20 },
      { name: "Shortsword", quantity: 1 },
      { name: "Dungeoneer's Pack", quantity: 1 }
    ]
  },
  {
    name: "Zara Moonwhisper",
    race: "Human",
    character_class: "Wizard",
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
      { name: "Spellbook", quantity: 1 },
      { name: "Dagger", quantity: 1 },
      { name: "Component Pouch", quantity: 1 },
      { name: "Scholar's Pack", quantity: 1 }
    ]
  },
  {
    name: "Brother Marcus",
    race: "Human",
    character_class: "Cleric",
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
      { name: "Chain Mail", quantity: 1 },
      { name: "Shield", quantity: 1 },
      { name: "Mace", quantity: 1 },
      { name: "Priest's Pack", quantity: 1 },
      { name: "Holy Symbol", quantity: 1 }
    ]
  },
  {
    name: "Shadowstep",
    race: "Halfling",
    character_class: "Rogue",
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
      { name: "Leather Armor", quantity: 1 },
      { name: "Shortsword", quantity: 1 },
      { name: "Dagger", quantity: 2 },
      { name: "Thieves' Tools", quantity: 1 },
      { name: "Burglar's Pack", quantity: 1 }
    ]
  },
  {
    name: "Seraphina Brightflame",
    race: "Dragonborn",
    character_class: "Paladin",
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
      { name: "Chain Mail", quantity: 1 },
      { name: "Shield", quantity: 1 },
      { name: "Longsword", quantity: 1 },
      { name: "Javelin", quantity: 5 },
      { name: "Explorer's Pack", quantity: 1 }
    ]
  }
];