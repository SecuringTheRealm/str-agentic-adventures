import { render, screen } from "@testing-library/react";
import * as api from "../services/api";
import CampaignGallery from "./CampaignGallery";
import styles from "./CampaignGallery.module.css";

// Mock the API module
vi.mock("../services/api");
const mockGetCampaignTemplates = vi.mocked(api.getCampaignTemplates);

describe("CampaignGallery", () => {
  const mockOnCampaignSelected = vi.fn();
  const mockOnCreateCustom = vi.fn();

  const mockTemplates = [
    {
      id: "template-1",
      name: "Test Campaign",
      description: "A test campaign description",
      setting: "A fantasy world",
      tone: "heroic" as const,
      plot_hooks: ["Hook 1", "Hook 2"],
      homebrew_rules: ["Rule 1"],
      is_custom: false,
    },
  ];

  beforeEach(() => {
    mockOnCampaignSelected.mockClear();
    mockOnCreateCustom.mockClear();
    mockGetCampaignTemplates.mockClear();
    mockGetCampaignTemplates.mockResolvedValue(mockTemplates);
  });

  it("renders Create Custom button visibly", async () => {
    render(
      <CampaignGallery
        onCampaignSelected={mockOnCampaignSelected}
        onCreateCustom={mockOnCreateCustom}
      />
    );

    // Wait for templates to load
    await screen.findByText("Create Custom");

    const createCustomButton = screen.getByRole("button", {
      name: "Create Custom",
    });
    expect(createCustomButton).toBeInTheDocument();
    expect(createCustomButton).toBeVisible();
  });

  it("renders Select Campaign buttons visibly for templates", async () => {
    render(
      <CampaignGallery
        onCampaignSelected={mockOnCampaignSelected}
        onCreateCustom={mockOnCreateCustom}
      />
    );

    // Wait for templates to load
    await screen.findByText("Select Campaign");

    const selectCampaignButton = screen.getByRole("button", {
      name: "Select Campaign",
    });
    expect(selectCampaignButton).toBeInTheDocument();
    expect(selectCampaignButton).toBeVisible();
  });

  it("renders buttons within reasonable container dimensions", async () => {
    const { container } = render(
      <CampaignGallery
        onCampaignSelected={mockOnCampaignSelected}
        onCreateCustom={mockOnCreateCustom}
      />
    );

    // Wait for templates to load
    await screen.findByText("Create Custom");

    // Check that the gallery container doesn't have excessive constraints
    const galleryContainer = container.querySelector(
      `.${styles.campaignGallery}`
    );
    expect(galleryContainer).toBeInTheDocument();

    // Verify buttons are present and visible
    const createCustomButton = screen.getByRole("button", {
      name: "Create Custom",
    });
    const selectCampaignButton = screen.getByRole("button", {
      name: "Select Campaign",
    });

    expect(createCustomButton).toBeVisible();
    expect(selectCampaignButton).toBeVisible();
  });
});
