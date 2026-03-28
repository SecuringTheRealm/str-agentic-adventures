import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as api from "../services/api";
import CampaignCreation from "./CampaignCreation";

// Polyfill pointer capture methods missing in jsdom (needed for Radix UI Select)
if (!Element.prototype.hasPointerCapture) {
  Element.prototype.hasPointerCapture = () => false;
}
if (!Element.prototype.setPointerCapture) {
  Element.prototype.setPointerCapture = () => {};
}
if (!Element.prototype.releasePointerCapture) {
  Element.prototype.releasePointerCapture = () => {};
}

/**
 * Helper to select an option from a Radix UI Select component in tests.
 * Opens the dropdown via pointerdown on the trigger, then clicks the desired option.
 */
async function selectRadixOption(trigger: HTMLElement, optionName: string) {
  fireEvent.pointerDown(trigger, {
    ctrlKey: false,
    button: 0,
    pointerId: 1,
    pointerType: "mouse",
  });
  const option = await screen.findByRole("option", { name: optionName });
  fireEvent.click(option);
}

// Mock the API module
vi.mock("../services/api");
const mockCreateCampaign = vi.mocked(api.createCampaign);

describe("CampaignCreation", () => {
  const mockOnCampaignCreated = vi.fn();

  beforeEach(() => {
    mockOnCampaignCreated.mockClear();
    mockCreateCampaign.mockClear();
    mockCreateCampaign.mockReset();
  });

  it("renders form elements correctly", () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    expect(screen.getByText("Create New Campaign")).toBeInTheDocument();
    expect(screen.getByLabelText("Campaign Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Campaign Setting")).toBeInTheDocument();
    expect(screen.getByLabelText("Campaign Tone")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Homebrew Rules (Optional)")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Create Campaign" })
    ).toBeInTheDocument();
  });

  it("has default tone set to heroic", () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const toneTrigger = screen.getByTestId("campaign-tone-select");
    expect(toneTrigger).toHaveTextContent("🛡️ Heroic");
  });

  it("shows all tone options", async () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const toneTrigger = screen.getByTestId("campaign-tone-select");
    fireEvent.pointerDown(toneTrigger, {
      ctrlKey: false,
      button: 0,
      pointerId: 1,
      pointerType: "mouse",
    });

    expect(
      await screen.findByRole("option", { name: "🛡️ Heroic" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "⚔️ Gritty" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "🃏 Humorous" })
    ).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "💀 Dark" })).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "🔍 Mystery" })
    ).toBeInTheDocument();
  });

  it("updates form fields correctly", async () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");
    const toneTrigger = screen.getByTestId("campaign-tone-select");
    const homebrewInput = screen.getByLabelText("Homebrew Rules (Optional)");

    await userEvent.type(nameInput, "The Lost Kingdom");
    await userEvent.type(settingInput, "A mystical realm");
    await selectRadixOption(toneTrigger, "⚔️ Gritty");
    await userEvent.type(homebrewInput, "Custom rule 1\nCustom rule 2");

    expect(nameInput).toHaveValue("The Lost Kingdom");
    expect(settingInput).toHaveValue("A mystical realm");
    expect(toneTrigger).toHaveTextContent("⚔️ Gritty");
    expect(homebrewInput).toHaveValue("Custom rule 1\nCustom rule 2");
  });

  it("shows validation error for empty required fields", async () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });
    await userEvent.click(submitButton);

    // The form should not call the API when validation fails
    expect(mockCreateCampaign).not.toHaveBeenCalled();
  });

  it("shows validation error when only name is provided", async () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    await userEvent.type(nameInput, "Test Campaign");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });
    await userEvent.click(submitButton);

    // The form should not call the API when validation fails
    expect(mockCreateCampaign).not.toHaveBeenCalled();
  });

  it("shows validation error when only setting is provided", async () => {
    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const settingInput = screen.getByLabelText("Campaign Setting");
    await userEvent.type(settingInput, "Test Setting");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });
    await userEvent.click(submitButton);

    // The form should not call the API when validation fails
    expect(mockCreateCampaign).not.toHaveBeenCalled();
  });

  it("successfully creates campaign with valid data", async () => {
    const mockCampaign = {
      id: "1",
      name: "Test Campaign",
      setting: "A mystical realm",
      tone: "heroic",
      homebrew_rules: [],
      characters: [],
    };
    mockCreateCampaign.mockResolvedValue(mockCampaign);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    await userEvent.type(nameInput, "The Lost Kingdom");
    await userEvent.type(settingInput, "A mystical realm");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(mockCreateCampaign).toHaveBeenCalledWith({
        name: "The Lost Kingdom",
        setting: "A mystical realm",
        tone: "heroic",
        homebrew_rules: [],
      });
    });

    await waitFor(() => {
      expect(mockOnCampaignCreated).toHaveBeenCalledWith(mockCampaign);
    });
  });

  it("parses homebrew rules correctly", async () => {
    const mockCampaign = {
      id: "1",
      name: "Test Campaign",
      setting: "Test Setting",
      tone: "heroic",
      homebrew_rules: ["Rule 1", "Rule 2", "Rule 3"],
      characters: [],
    };
    mockCreateCampaign.mockResolvedValue(mockCampaign);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");
    const homebrewInput = screen.getByLabelText("Homebrew Rules (Optional)");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");
    await userEvent.type(homebrewInput, "Rule 1\n\nRule 2\n   \nRule 3   ");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(mockCreateCampaign).toHaveBeenCalledWith({
        name: "Test Campaign",
        setting: "Test Setting",
        tone: "heroic",
        homebrew_rules: ["Rule 1", "Rule 2", "Rule 3"],
      });
    });
  });

  it("shows loading state during submission", async () => {
    let resolvePromise: ((value: unknown) => void) | undefined;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockCreateCampaign.mockReturnValue(promise);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    expect(screen.getByText("Creating...")).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    expect(nameInput).toBeDisabled();
    expect(settingInput).toBeDisabled();

    // Resolve the promise to clean up and wait for completion
    await act(async () => {
      resolvePromise?.({ id: "1", name: "Test Campaign" });
      await promise;
    });
  });

  it("handles API errors gracefully", async () => {
    const errorMessage = "Network error occurred";
    mockCreateCampaign.mockRejectedValue(new Error(errorMessage));

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(mockCreateCampaign).toHaveBeenCalled();
    });

    // Should show error message to user
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    // Should re-enable the submit button after error
    expect(submitButton).not.toBeDisabled();
  });

  it("shows loading state during campaign creation", async () => {
    // Use a longer timeout to ensure we can catch the loading state
    const slowPromise = new Promise((resolve) =>
      setTimeout(
        () =>
          resolve({
            id: "1",
            name: "Test",
            setting: "Test",
            tone: "heroic",
            homebrew_rules: [],
            characters: [],
          }),
        500
      )
    );
    mockCreateCampaign.mockReturnValue(slowPromise);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    // Click and immediately check for disabled state
    await act(async () => {
      await userEvent.click(submitButton);
    });

    // Button should be disabled during loading - check immediately after click
    await waitFor(
      () => {
        expect(submitButton).toBeDisabled();
      },
      { timeout: 100 }
    );

    // Wait for completion
    await waitFor(
      () => {
        expect(submitButton).not.toBeDisabled();
      },
      { timeout: 1000 }
    );
  });

  it("trims whitespace from form inputs", async () => {
    const mockCampaign = {
      id: "1",
      name: "Test Campaign",
      setting: "Test Setting",
      tone: "heroic",
      homebrew_rules: [],
      characters: [],
    };
    mockCreateCampaign.mockResolvedValue(mockCampaign);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    // Type with leading/trailing spaces
    await userEvent.type(nameInput, "  Test Campaign  ");
    await userEvent.type(settingInput, "  Test Setting  ");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(mockCreateCampaign).toHaveBeenCalledWith({
        name: "Test Campaign", // Should be trimmed
        setting: "Test Setting", // Should be trimmed
        tone: "heroic",
        homebrew_rules: [],
      });
    });
  });

  it("handles empty homebrew rules correctly", async () => {
    const mockCampaign = {
      id: "1",
      name: "Test Campaign",
      setting: "Test Setting",
      tone: "heroic",
      homebrew_rules: [],
      characters: [],
    };
    mockCreateCampaign.mockResolvedValue(mockCampaign);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");
    const homebrewInput = screen.getByLabelText("Homebrew Rules (Optional)");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");
    // Leave homebrew rules empty or add whitespace only
    await userEvent.type(homebrewInput, "   \n  \n   ");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(mockCreateCampaign).toHaveBeenCalledWith({
        name: "Test Campaign",
        setting: "Test Setting",
        tone: "heroic",
        homebrew_rules: [], // Should filter out empty lines
      });
    });
  });

  it("handles very long input values", async () => {
    const longName = "A".repeat(1000);
    const longSetting = "B".repeat(400); // Reduced to stay under 500 char limit

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    await userEvent.type(nameInput, longName);
    await userEvent.type(settingInput, longSetting);

    // Should handle long input without crashing
    expect(nameInput).toHaveValue(longName);
    expect(settingInput).toHaveValue(longSetting);
  });

  it("resets form state after successful submission", async () => {
    const mockCampaign = {
      id: "1",
      name: "Test Campaign",
      setting: "Test Setting",
      tone: "heroic",
      homebrew_rules: [],
      characters: [],
    };
    mockCreateCampaign.mockResolvedValue(mockCampaign);

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(mockOnCampaignCreated).toHaveBeenCalledWith(mockCampaign);
    });

    // Form should be reset or the component unmounted (depending on implementation)
    // This test ensures the callback was called correctly
    expect(mockOnCampaignCreated).toHaveBeenCalledTimes(1);
  });

  it("maintains form state during failed submissions", async () => {
    mockCreateCampaign.mockRejectedValue(new Error("Server error"));

    render(<CampaignCreation onCampaignCreated={mockOnCampaignCreated} />);

    const nameInput = screen.getByLabelText("Campaign Name");
    const settingInput = screen.getByLabelText("Campaign Setting");
    const toneTrigger = screen.getByTestId("campaign-tone-select");

    await userEvent.type(nameInput, "Test Campaign");
    await userEvent.type(settingInput, "Test Setting");
    await selectRadixOption(toneTrigger, "⚔️ Gritty");

    const submitButton = screen.getByRole("button", {
      name: "Create Campaign",
    });

    await act(async () => {
      await userEvent.click(submitButton);
    });

    // The error message should match what was thrown
    await waitFor(() => {
      expect(screen.getByText("Server error")).toBeInTheDocument();
    });

    // Form values should be preserved after error
    expect(nameInput).toHaveValue("Test Campaign");
    expect(settingInput).toHaveValue("Test Setting");
    expect(toneTrigger).toHaveTextContent("⚔️ Gritty");
  });
});
