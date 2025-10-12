import { render, screen } from "@testing-library/react";
import App from "./App";

// Mock all API calls to avoid network issues in tests
vi.mock("../services/api", () => ({
  getCampaignTemplates: vi.fn().mockResolvedValue([]),
  getCampaigns: vi.fn().mockResolvedValue({ campaigns: [] }),
  createCampaign: vi.fn(),
  deleteCampaign: vi.fn(),
  cloneCampaign: vi.fn(),
}));

describe("App Campaign Setup Layout", () => {
  it("should not constrain campaign gallery width excessively", () => {
    render(<App />);

    // Find the campaign setup container
    const campaignSetup = document.querySelector(".campaign-setup");
    expect(campaignSetup).toBeInTheDocument();

    // Get computed styles
    const styles = window.getComputedStyle(campaignSetup as Element);

    // The max-width should be reasonable for campaign gallery layout
    // Should not have the problematic 600px constraint, but should have a reasonable limit
    const maxWidth = styles.maxWidth;

    // Should not have the problematic 600px constraint
    expect(maxWidth).not.toBe("600px");
    // Should have a reasonable constraint that allows for proper grid layout
    expect(maxWidth).toBe("1400px");
  });

  it("should allow campaign gallery to use available space", async () => {
    render(<App />);

    // Wait for campaign hub to appear
    await screen.findByText("Campaign Hub");

    // The campaign gallery should have enough space for proper layout
    const campaignGallery = document.querySelector(".campaign-gallery");
    if (campaignGallery) {
      const styles = window.getComputedStyle(campaignGallery);
      // Gallery should not be constrained by a small max-width
      expect(styles.maxWidth).not.toBe("600px");
    }
  });
});
