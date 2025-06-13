import React, { useState } from 'react';
import { Character, CharacterCreateRequest, createCharacter } from '../services/api';
import './CharacterCreation.css';

interface CharacterCreationProps {
  onCharacterCreated: (character: Character) => void;
  onCancel: () => void;
}

const CharacterCreation: React.FC<CharacterCreationProps> = ({ 
  onCharacterCreated, 
  onCancel 
}) => {
  const [formData, setFormData] = useState<CharacterCreateRequest>({
    name: '',
    race: 'Human',
    character_class: 'Fighter',
    abilities: {
      strength: 10,
      dexterity: 10,
      constitution: 10,
      intelligence: 10,
      wisdom: 10,
      charisma: 10
    },
    backstory: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Common D&D races and classes
  const races = [
    'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 
    'Half-Elf', 'Half-Orc', 'Tiefling'
  ];

  const classes = [
    'Fighter', 'Wizard', 'Cleric', 'Rogue', 'Ranger', 'Paladin',
    'Barbarian', 'Bard', 'Druid', 'Monk', 'Sorcerer', 'Warlock'
  ];

  const handleInputChange = (field: string, value: string | number) => {
    if (field.startsWith('abilities.')) {
      const abilityName = field.split('.')[1];
      setFormData(prev => ({
        ...prev,
        abilities: {
          ...prev.abilities,
          [abilityName]: Number(value)
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Character name is required';
    }

    if (!formData.race) {
      errors.race = 'Race is required';
    }

    if (!formData.character_class) {
      errors.character_class = 'Class is required';
    }

    // Validate ability scores (typically 3-18 for D&D)
    Object.entries(formData.abilities).forEach(([ability, score]) => {
      if (score < 3 || score > 18) {
        errors[`abilities.${ability}`] = 'Ability scores must be between 3 and 18';
      }
    });

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const character = await createCharacter(formData);
      onCharacterCreated(character);
    } catch (err) {
      console.error('Error creating character:', err);
      setError('Failed to create character. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRandomizeAbilities = () => {
    // Generate random ability scores using 4d6 drop lowest method (simplified to 8-18 range)
    const randomAbilities = {
      strength: Math.floor(Math.random() * 11) + 8,
      dexterity: Math.floor(Math.random() * 11) + 8,
      constitution: Math.floor(Math.random() * 11) + 8,
      intelligence: Math.floor(Math.random() * 11) + 8,
      wisdom: Math.floor(Math.random() * 11) + 8,
      charisma: Math.floor(Math.random() * 11) + 8
    };
    
    setFormData(prev => ({
      ...prev,
      abilities: randomAbilities
    }));
  };

  return (
    <div className="character-creation">
      <div className="creation-header">
        <h2>Create Your Character</h2>
        <button type="button" onClick={onCancel} className="cancel-button">
          ← Back to Campaigns
        </button>
      </div>

      <form onSubmit={handleSubmit} className="character-form">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-group">
            <label htmlFor="name">Character Name *</label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className={validationErrors.name ? 'error' : ''}
              placeholder="Enter your character's name"
            />
            {validationErrors.name && (
              <span className="field-error">{validationErrors.name}</span>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="race">Race *</label>
              <select
                id="race"
                value={formData.race}
                onChange={(e) => handleInputChange('race', e.target.value)}
                className={validationErrors.race ? 'error' : ''}
              >
                {races.map(race => (
                  <option key={race} value={race}>{race}</option>
                ))}
              </select>
              {validationErrors.race && (
                <span className="field-error">{validationErrors.race}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="character_class">Class *</label>
              <select
                id="character_class"
                value={formData.character_class}
                onChange={(e) => handleInputChange('character_class', e.target.value)}
                className={validationErrors.character_class ? 'error' : ''}
              >
                {classes.map(cls => (
                  <option key={cls} value={cls}>{cls}</option>
                ))}
              </select>
              {validationErrors.character_class && (
                <span className="field-error">{validationErrors.character_class}</span>
              )}
            </div>
          </div>
        </div>

        <div className="form-section">
          <div className="abilities-header">
            <h3>Ability Scores</h3>
            <button
              type="button"
              onClick={handleRandomizeAbilities}
              className="randomize-button"
            >
              🎲 Randomize
            </button>
          </div>
          
          <div className="abilities-grid">
            {Object.entries(formData.abilities).map(([ability, score]) => (
              <div key={ability} className="ability-group">
                <label htmlFor={ability}>
                  {ability.charAt(0).toUpperCase() + ability.slice(1)}
                </label>
                <input
                  type="number"
                  id={ability}
                  min="3"
                  max="18"
                  value={score}
                  onChange={(e) => handleInputChange(`abilities.${ability}`, e.target.value)}
                  className={validationErrors[`abilities.${ability}`] ? 'error' : ''}
                />
                {validationErrors[`abilities.${ability}`] && (
                  <span className="field-error">{validationErrors[`abilities.${ability}`]}</span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="form-section">
          <div className="form-group">
            <label htmlFor="backstory">Backstory (Optional)</label>
            <textarea
              id="backstory"
              value={formData.backstory}
              onChange={(e) => handleInputChange('backstory', e.target.value)}
              placeholder="Tell us about your character's background, motivations, and personality..."
              rows={4}
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="secondary-button"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="primary-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating Character...' : 'Create Character'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CharacterCreation;