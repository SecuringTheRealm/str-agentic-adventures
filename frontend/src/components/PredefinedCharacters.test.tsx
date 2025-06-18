import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import PredefinedCharacters from './PredefinedCharacters';
import styles from "./PredefinedCharacters.module.css";

describe('PredefinedCharacters', () => {
  const mockOnCharacterSelected = vi.fn();
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders predefined characters list', () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    expect(screen.getByText('Choose a Pre-Defined Character')).toBeInTheDocument();
    expect(screen.getByText('Thorin Ironforge')).toBeInTheDocument();
    expect(screen.getByText('Lyralei Swiftarrow')).toBeInTheDocument();
    expect(screen.getByText('Zara Moonwhisper')).toBeInTheDocument();
  });

  it('displays character details correctly', () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    // Check for character basics
    expect(screen.getByText('Level 1 dwarf fighter')).toBeInTheDocument();
    expect(screen.getByText('Level 1 elf ranger')).toBeInTheDocument();
    
    // Check for ability scores
    expect(screen.getAllByText('STR')).toHaveLength(6); // 6 characters
    expect(screen.getAllByText('DEX')).toHaveLength(6);
  });

  it('calls onBack when back button is clicked', () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    const backButton = screen.getByRole('button', { name: '← Back to Character Options' });
    fireEvent.click(backButton);
    
    expect(mockOnBack).toHaveBeenCalledTimes(1);
  });

  it('calls onCharacterSelected when character is selected', () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    const selectButtons = screen.getAllByText('Select This Character');
    fireEvent.click(selectButtons[0]);
    
    expect(mockOnCharacterSelected).toHaveBeenCalledTimes(1);
    expect(mockOnCharacterSelected).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Thorin Ironforge',
        race: 'dwarf',
        character_class: 'fighter',
        id: expect.any(String)
      })
    );
  });
});