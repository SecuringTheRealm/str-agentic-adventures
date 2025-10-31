/**
 * D&D 5e SRD-compliant test data constants
 * These values match the SRD (Systems Reference Document) requirements
 * and must be kept in sync with backend validation rules.
 */

// Valid D&D 5e SRD races (lowercase for API)
export const VALID_RACES = [
  'human',
  'elf',
  'dwarf',
  'halfling',
  'dragonborn',
  'gnome',
  'half-elf',
  'half-orc',
  'tiefling',
] as const;

// Valid D&D 5e SRD classes (lowercase for API)
export const VALID_CLASSES = [
  'barbarian',
  'bard',
  'cleric',
  'druid',
  'fighter',
  'monk',
  'paladin',
  'ranger',
  'rogue',
  'sorcerer',
  'warlock',
  'wizard',
] as const;

// Valid campaign tones
export const VALID_TONES = [
  'heroic',
  'dark',
  'lighthearted',
  'gritty',
  'mysterious',
] as const;

// Ability score constraints
export const ABILITY_SCORE_RULES = {
  total: 78, // Standard point buy equivalent with racial bonuses
  min: 3,
  max: 20,
  defaultStarting: 13,
} as const;

// Test character templates
export const TEST_CHARACTERS = {
  elf_ranger: {
    name: 'Eldrin Shadowblade',
    race: 'elf' as const,
    character_class: 'ranger' as const,
    abilities: {
      strength: 13,
      dexterity: 16,
      constitution: 13,
      intelligence: 12,
      wisdom: 14,
      charisma: 10,
    },
    backstory:
      'A skilled ranger from the Moonwood, trained in tracking and survival. Seeks to protect the forest realm from encroaching darkness.',
  },
  dwarf_fighter: {
    name: 'Thorin Ironbeard',
    race: 'dwarf' as const,
    character_class: 'fighter' as const,
    abilities: {
      strength: 16,
      dexterity: 12,
      constitution: 15,
      intelligence: 10,
      wisdom: 13,
      charisma: 12,
    },
    backstory:
      'A veteran warrior from the mountain clans, skilled in combat and loyal to his companions.',
  },
  human_wizard: {
    name: 'Aria Spellweaver',
    race: 'human' as const,
    character_class: 'wizard' as const,
    abilities: {
      strength: 10,
      dexterity: 13,
      constitution: 13,
      intelligence: 16,
      wisdom: 14,
      charisma: 12,
    },
    backstory:
      'A talented mage from the Academy of Arcane Arts, dedicated to mastering the mystical forces.',
  },
} as const;

// Test campaign templates
export const TEST_CAMPAIGNS = {
  heroic_fantasy: {
    name: 'Test Campaign - Heroic Quest',
    setting:
      'A mysterious forest realm filled with ancient magic and hidden dangers',
    tone: 'heroic' as const,
    homebrew_rules: [],
  },
  dark_adventure: {
    name: 'Test Campaign - Dark Shadows',
    setting: 'A gothic realm where darkness threatens to consume all light',
    tone: 'dark' as const,
    homebrew_rules: ['Critical hits deal maximum damage', 'No death saves'],
  },
  mystery_investigation: {
    name: 'Test Campaign - Mystery Manor',
    setting: 'An investigation into strange occurrences at an old estate',
    tone: 'mysterious' as const,
    homebrew_rules: ['Advantage on investigation checks'],
  },
} as const;

// Type exports for TypeScript
export type ValidRace = (typeof VALID_RACES)[number];
export type ValidClass = (typeof VALID_CLASSES)[number];
export type ValidTone = (typeof VALID_TONES)[number];
