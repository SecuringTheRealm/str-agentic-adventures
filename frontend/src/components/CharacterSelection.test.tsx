import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import CharacterSelection from './CharacterSelection';
import type { Campaign } from '../services/api';
import styles from "./CharacterSelection.module.css";

describe('CharacterSelection', () => {
  const mockCampaign: Campaign = {
    id: '1',
    name: 'Test Campaign',
    setting: 'Fantasy',
    tone: 'Heroic',
    homebrew_rules: [],
    characters: []
  };

  const mockOnCharacterSelected = vi.fn();
  const mockOnBackToCampaigns = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders campaign name and character options', () => {
    render(
      <CharacterSelection
        campaign={mockCampaign}
        onCharacterSelected={mockOnCharacterSelected}
        onBackToCampaigns={mockOnBackToCampaigns}
      />
    );

    expect(screen.getByText('Choose Your Character')).toBeInTheDocument();
    expect(screen.getByText('Test Campaign')).toBeInTheDocument();
    expect(screen.getByText('Create New Character')).toBeInTheDocument();
    expect(screen.getByText('Choose Pre-Defined Character')).toBeInTheDocument();
  });

  it('shows create character button', () => {
    render(
      <CharacterSelection
        campaign={mockCampaign}
        onCharacterSelected={mockOnCharacterSelected}
        onBackToCampaigns={mockOnBackToCampaigns}
      />
    );

    const createButton = screen.getByRole('button', { name: 'Create Character' });
    expect(createButton).toBeInTheDocument();
  });

  it('shows browse characters button', () => {
    render(
      <CharacterSelection
        campaign={mockCampaign}
        onCharacterSelected={mockOnCharacterSelected}
        onBackToCampaigns={mockOnBackToCampaigns}
      />
    );

    const browseButton = screen.getByRole('button', { name: 'Browse Characters' });
    expect(browseButton).toBeInTheDocument();
  });

  it('calls onBackToCampaigns when back button is clicked', () => {
    render(
      <CharacterSelection
        campaign={mockCampaign}
        onCharacterSelected={mockOnCharacterSelected}
        onBackToCampaigns={mockOnBackToCampaigns}
      />
    );

    const backButton = screen.getByRole('button', { name: '← Back to Campaigns' });
    fireEvent.click(backButton);
    
    expect(mockOnBackToCampaigns).toHaveBeenCalledTimes(1);
  });
});