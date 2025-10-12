import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import * as api from "../services/api";
import CampaignEditor from "./CampaignEditor";
import styles from "./CampaignEditor.module.css";

// Mock the API module
vi.mock("../services/api");
const mockUpdateCampaign = vi.mocked(api.updateCampaign);
const mockGetAIAssistance = vi.mocked(api.getAIAssistance);
const mockGenerateAIContent = vi.mocked(api.generateAIContent);

const mockCampaign = {
  id: "test-campaign-id",
  name: "Test Campaign",
  setting: "A magical forest",
  tone: "heroic",
  homebrew_rules: ["Custom rule 1"],
  characters: [],
  description: "A test campaign",
  world_description: "A magical world",
};

describe("CampaignEditor", () => {
  const mockOnCampaignSaved = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    mockOnCampaignSaved.mockClear();
    mockOnCancel.mockClear();
    mockUpdateCampaign.mockClear();
    mockGetAIAssistance.mockClear();
    mockGenerateAIContent.mockClear();
    mockUpdateCampaign.mockReset();
    mockGetAIAssistance.mockReset();
    mockGenerateAIContent.mockReset();
  });

  it("renders AI assistance button for description field", () => {
    render(
      <CampaignEditor
        campaign={mockCampaign}
        onCampaignSaved={mockOnCampaignSaved}
        onCancel={mockOnCancel}
      />
    );

    // Find the AI assistance button for description field
    const aiButtons = screen.getAllByText("✨ AI");
    expect(aiButtons.length).toBeGreaterThan(0);
  });

  it("shows AI suggestions when AI button is clicked", async () => {
    mockGetAIAssistance.mockResolvedValue({
      suggestions: [
        "Expand on character motivations",
        "Add more dialogue or character interactions",
      ],
    });

    render(
      <CampaignEditor
        campaign={mockCampaign}
        onCampaignSaved={mockOnCampaignSaved}
        onCancel={mockOnCancel}
      />
    );

    // Click the AI assistance button for description
    const aiButtons = screen.getAllByText("✨ AI");
    await act(async () => {
      fireEvent.click(aiButtons[0]);
    });

    await waitFor(() => {
      expect(mockGetAIAssistance).toHaveBeenCalledWith({
        text: "A test campaign",
        context_type: "description",
        campaign_tone: "heroic",
      });
    });

    await waitFor(() => {
      expect(screen.getByText("✨ AI Writing Assistant")).toBeInTheDocument();
      expect(
        screen.getByText("Expand on character motivations")
      ).toBeInTheDocument();
    });
  });

  it("apply button is disabled for empty fields", async () => {
    // Create a campaign with empty description
    const emptyCampaign = { ...mockCampaign, description: "" };

    mockGetAIAssistance.mockResolvedValue({
      suggestions: ["Expand on character motivations"],
    });

    render(
      <CampaignEditor
        campaign={emptyCampaign}
        onCampaignSaved={mockOnCampaignSaved}
        onCancel={mockOnCancel}
      />
    );

    // Click the AI assistance button for description
    const aiButtons = screen.getAllByText("✨ AI");
    await act(async () => {
      fireEvent.click(aiButtons[0]);
    });

    await waitFor(() => {
      expect(
        screen.getByText("Expand on character motivations")
      ).toBeInTheDocument();
    });

    // The Apply button should be disabled for empty field
    const applyButton = screen.getByText("Apply");
    expect(applyButton).toBeDisabled();
  });

  it("calls generateAIContent when Apply button is clicked with non-empty field", async () => {
    mockGetAIAssistance.mockResolvedValue({
      suggestions: ["Expand on character motivations"],
    });

    mockGenerateAIContent.mockResolvedValue({
      generated_content:
        "The heroes are driven by a desire to protect the innocent and seek justice.",
      success: true,
    });

    render(
      <CampaignEditor
        campaign={mockCampaign}
        onCampaignSaved={mockOnCampaignSaved}
        onCancel={mockOnCancel}
      />
    );

    // Click the AI assistance button for description
    const aiButtons = screen.getAllByText("✨ AI");
    await act(async () => {
      fireEvent.click(aiButtons[0]);
    });

    await waitFor(() => {
      expect(
        screen.getByText("Expand on character motivations")
      ).toBeInTheDocument();
    });

    // Click the Apply button
    const applyButton = screen.getByText("Apply");
    await act(async () => {
      fireEvent.click(applyButton);
    });

    await waitFor(() => {
      expect(mockGenerateAIContent).toHaveBeenCalledWith({
        suggestion: "Expand on character motivations",
        current_text: "A test campaign",
        context_type: "description",
        campaign_tone: "heroic",
      });
    });
  });
});
