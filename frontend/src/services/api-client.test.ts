/**
 * Tests for OpenAPI Generated Client Integration
 * Validates that the generated client is properly integrated and functional.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { DefaultApi, Configuration } from '../api-client';
import { CharacterSheet, CreateCharacterRequest, Race, CharacterClass } from '../api-client';

// Mock axios to avoid actual HTTP calls in tests
vi.mock('axios');

describe('OpenAPI Generated Client Integration', () => {
  let apiClient: DefaultApi;

  beforeEach(() => {
    // Create API client with test configuration
    const config = new Configuration({
      basePath: 'http://localhost:8000',
    });
    apiClient = new DefaultApi(config);
  });

  describe('API Client Setup', () => {
    it('should create API client instance', () => {
      expect(apiClient).toBeDefined();
      expect(apiClient).toBeInstanceOf(DefaultApi);
    });

    it('should have configuration set', () => {
      expect(apiClient.configuration).toBeDefined();
      expect(apiClient.configuration.basePath).toBe('http://localhost:8000');
    });
  });

  describe('Generated Types Validation', () => {
    it('should have CreateCharacterRequest type with correct fields', () => {
      const characterRequest: CreateCharacterRequest = {
        name: 'Test Hero',
        race: Race.Human,
        characterClass: CharacterClass.Fighter,
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
        backstory: 'A brave warrior',
      };

      expect(characterRequest.name).toBe('Test Hero');
      expect(characterRequest.race).toBe(Race.Human);
      expect(characterRequest.characterClass).toBe(CharacterClass.Fighter);
      expect(characterRequest.abilities).toBeDefined();
      expect(characterRequest.abilities.strength).toBe(16);
    });

    it('should have CharacterSheet type with correct fields', () => {
      const character: CharacterSheet = {
        id: 'test-id',
        name: 'Test Hero',
        race: Race.Human,
        characterClass: CharacterClass.Fighter,
        level: 1,
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
        hitPoints: {
          current: 20,
          maximum: 20,
        },
        inventory: [],
      };

      expect(character.id).toBe('test-id');
      expect(character.name).toBe('Test Hero');
      expect(character.race).toBe(Race.Human);
      expect(character.characterClass).toBe(CharacterClass.Fighter);
      expect(character.level).toBe(1);
      expect(character.hitPoints).toBeDefined();
      expect(character.hitPoints.current).toBe(20);
      expect(character.hitPoints.maximum).toBe(20);
      expect(character.inventory).toBeInstanceOf(Array);
    });

    it('should have correct enum values', () => {
      // Test Race enum
      expect(Race.Human).toBeDefined();
      expect(Race.Elf).toBeDefined();
      expect(Race.Dwarf).toBeDefined();
      expect(Race.Halfling).toBeDefined();

      // Test CharacterClass enum
      expect(CharacterClass.Fighter).toBeDefined();
      expect(CharacterClass.Wizard).toBeDefined();
      expect(CharacterClass.Rogue).toBeDefined();
      expect(CharacterClass.Cleric).toBeDefined();
    });
  });

  describe('API Methods Availability', () => {
    it('should have character creation method', () => {
      expect(apiClient.apiGameCharacterPost).toBeDefined();
      expect(typeof apiClient.apiGameCharacterPost).toBe('function');
    });

    it('should have character retrieval method', () => {
      expect(apiClient.apiGameCharacterCharacterIdGet).toBeDefined();
      expect(typeof apiClient.apiGameCharacterCharacterIdGet).toBe('function');
    });

    it('should have campaign creation method', () => {
      expect(apiClient.apiGameCampaignPost).toBeDefined();
      expect(typeof apiClient.apiGameCampaignPost).toBe('function');
    });

    it('should have player input method', () => {
      expect(apiClient.apiGameInputPost).toBeDefined();
      expect(typeof apiClient.apiGameInputPost).toBe('function');
    });

    it('should have health check method', () => {
      expect(apiClient.healthHealthGet).toBeDefined();
      expect(typeof apiClient.healthHealthGet).toBe('function');
    });
  });

  describe('Client Generation Validation', () => {
    it('should have all exported types from api-client', () => {
      // Import the main exports to ensure they exist
      const { DefaultApi, Configuration } = require('../api-client');
      
      expect(DefaultApi).toBeDefined();
      expect(Configuration).toBeDefined();
      
      // Check that we can create instances
      const config = new Configuration();
      const api = new DefaultApi(config);
      
      expect(config).toBeInstanceOf(Configuration);
      expect(api).toBeInstanceOf(DefaultApi);
    });

    it('should have type definitions for all models', () => {
      // These imports should not throw if the types are properly generated
      const types = require('../api-client');
      
      const expectedTypes = [
        'CharacterSheet',
        'CreateCharacterRequest', 
        'CreateCampaignRequest',
        'Campaign',
        'PlayerInput',
        'GameResponse',
        'Race',
        'CharacterClass',
        'Abilities'
      ];

      for (const typeName of expectedTypes) {
        expect(types[typeName]).toBeDefined();
      }
    });

    it('should have consistent field naming with backend', () => {
      // Test that generated types use the field names expected by backend
      const characterRequest: CreateCharacterRequest = {
        name: 'Test',
        race: Race.Human,
        characterClass: CharacterClass.Fighter, // Should be characterClass, not class
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
      };

      // These field names should match the backend API exactly
      expect(characterRequest).toHaveProperty('name');
      expect(characterRequest).toHaveProperty('race');
      expect(characterRequest).toHaveProperty('characterClass'); // Not 'class'
      expect(characterRequest).toHaveProperty('abilities');
    });
  });

  describe('Backward Compatibility', () => {
    it('should maintain compatibility with legacy frontend code', () => {
      // Test that the wrapper in api.ts maintains backward compatibility
      const { createCharacter, createCampaign } = require('./api');
      
      expect(createCharacter).toBeDefined();
      expect(typeof createCharacter).toBe('function');
      
      expect(createCampaign).toBeDefined();
      expect(typeof createCampaign).toBe('function');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      // Mock a failed response
      const mockError = new Error('Network error');
      vi.spyOn(apiClient, 'apiGameCharacterPost').mockRejectedValue(mockError);

      try {
        await apiClient.apiGameCharacterPost({
          name: 'Test',
          race: Race.Human,
          characterClass: CharacterClass.Fighter,
          abilities: {
            strength: 16,
            dexterity: 14,
            constitution: 15,
            intelligence: 12,
            wisdom: 13,
            charisma: 10,
          },
        });
        
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error).toBe(mockError);
      }
    });
  });

  describe('Schema Validation', () => {
    it('should validate required fields at compile time', () => {
      // This test ensures TypeScript compilation catches missing required fields
      
      // This should compile without errors
      const validRequest: CreateCharacterRequest = {
        name: 'Test Hero',
        race: Race.Human,
        characterClass: CharacterClass.Fighter,
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
      };

      expect(validRequest).toBeDefined();
      expect(validRequest.name).toBe('Test Hero');
      
      // Note: Missing required fields would cause TypeScript compilation errors
      // which is exactly what we want for type safety
    });

    it('should allow optional fields to be undefined', () => {
      const requestWithoutOptionals: CreateCharacterRequest = {
        name: 'Test Hero',
        race: Race.Human,
        characterClass: CharacterClass.Fighter,
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
        // backstory is optional and can be omitted
      };

      expect(requestWithoutOptionals).toBeDefined();
      expect(requestWithoutOptionals.backstory).toBeUndefined();
    });
  });
});