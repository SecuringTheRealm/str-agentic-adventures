import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatBox from "./ChatBox";
import styles from "./ChatBox.module.css";

// Mock scrollIntoView
Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
  value: vi.fn(),
  writable: true,
});

describe("ChatBox", () => {
  const mockOnSendMessage = vi.fn();
  const defaultProps = {
    messages: [],
    onSendMessage: mockOnSendMessage,
    isLoading: false,
  };

  beforeEach(() => {
    mockOnSendMessage.mockClear();
  });

  it("renders empty chat box", () => {
    render(<ChatBox {...defaultProps} />);
    expect(
      screen.getByPlaceholderText("What do you want to do?")
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
  });

  it("displays messages correctly", () => {
    const messages = [
      { text: "Hello player!", sender: "dm" as const },
      { text: "Hello DM!", sender: "player" as const },
    ];

    render(<ChatBox {...defaultProps} messages={messages} />);

    expect(screen.getByText("Hello player!")).toBeInTheDocument();
    expect(screen.getByText("Hello DM!")).toBeInTheDocument();
    expect(screen.getByText("Dungeon Master")).toBeInTheDocument();
    expect(screen.getByText("You")).toBeInTheDocument();
  });

  it("handles message input and submission", async () => {
    render(<ChatBox {...defaultProps} />);

    const input = screen.getByPlaceholderText("What do you want to do?");
    const sendButton = screen.getByRole("button", { name: "Send" });

    // Type a message
    await userEvent.type(input, "I want to explore the castle");
    expect(input).toHaveValue("I want to explore the castle");

    // Submit the message
    await userEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith(
      "I want to explore the castle"
    );
    expect(input).toHaveValue(""); // Input should be cleared
  });

  it("handles form submission with Enter key", async () => {
    render(<ChatBox {...defaultProps} />);

    const input = screen.getByPlaceholderText("What do you want to do?");

    await userEvent.type(input, "Look around");
    await userEvent.keyboard("{Enter}");

    expect(mockOnSendMessage).toHaveBeenCalledWith("Look around");
    expect(input).toHaveValue("");
  });

  it("disables input and button when loading", () => {
    render(<ChatBox {...defaultProps} isLoading={true} />);

    const input = screen.getByPlaceholderText("What do you want to do?");
    const sendButton = screen.getByRole("button", { name: "Send" });

    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it("disables send button when input is empty", () => {
    render(<ChatBox {...defaultProps} />);

    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(sendButton).toBeDisabled();
  });

  it("disables send button when input is only whitespace", async () => {
    render(<ChatBox {...defaultProps} />);

    const input = screen.getByPlaceholderText("What do you want to do?");
    const sendButton = screen.getByRole("button", { name: "Send" });

    await userEvent.type(input, "   ");
    expect(sendButton).toBeDisabled();
  });

  it("does not submit empty or whitespace-only messages", async () => {
    render(<ChatBox {...defaultProps} />);

    const input = screen.getByPlaceholderText("What do you want to do?");

    // Try to submit empty message
    await userEvent.keyboard("{Enter}");
    expect(mockOnSendMessage).not.toHaveBeenCalled();

    // Try to submit whitespace-only message
    await userEvent.type(input, "   ");
    await userEvent.keyboard("{Enter}");
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it("shows loading indicator when loading", () => {
    render(<ChatBox {...defaultProps} isLoading={true} />);

    expect(screen.getByText("Dungeon Master")).toBeInTheDocument();
    // Look for the typing indicator by its class
    expect(
      document.querySelector(`.${styles.typingIndicator}`)
    ).toBeInTheDocument();
  });

  it("prevents submission when loading", async () => {
    render(<ChatBox {...defaultProps} isLoading={true} />);

    const input = screen.getByPlaceholderText("What do you want to do?");

    // Input should be disabled, but let's test the form anyway
    fireEvent.change(input, { target: { value: "test message" } });
    fireEvent.submit(input.closest("form") as HTMLFormElement);

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it("applies correct CSS classes to messages", () => {
    const messages = [
      { text: "DM message", sender: "dm" as const },
      { text: "Player message", sender: "player" as const },
    ];

    render(<ChatBox {...defaultProps} messages={messages} />);

    const dmMessage = screen
      .getByText("DM message")
      .closest(`.${styles.message}`);
    const playerMessage = screen
      .getByText("Player message")
      .closest(`.${styles.message}`);

    expect(dmMessage).toHaveClass(styles.dmMessage);
    expect(playerMessage).toHaveClass(styles.playerMessage);
  });

  it("renders suggested action buttons when provided", () => {
    const actions = [
      "Explore the dungeon",
      "Talk to the innkeeper",
      "Check your map",
    ];
    render(
      <ChatBox
        {...defaultProps}
        suggestedActions={actions}
        onSuggestedAction={mockOnSendMessage}
      />
    );

    expect(screen.getByTestId("suggested-actions")).toBeInTheDocument();
    expect(screen.getByText("Explore the dungeon")).toBeInTheDocument();
    expect(screen.getByText("Talk to the innkeeper")).toBeInTheDocument();
    expect(screen.getByText("Check your map")).toBeInTheDocument();
  });

  it("does not render suggested actions section when list is empty", () => {
    render(<ChatBox {...defaultProps} suggestedActions={[]} />);
    expect(screen.queryByTestId("suggested-actions")).not.toBeInTheDocument();
  });

  it("does not render suggested actions section when prop is not provided", () => {
    render(<ChatBox {...defaultProps} />);
    expect(screen.queryByTestId("suggested-actions")).not.toBeInTheDocument();
  });

  it("sends suggested action when action button is clicked", async () => {
    const actions = ["Investigate the area"];
    render(
      <ChatBox
        {...defaultProps}
        suggestedActions={actions}
        onSuggestedAction={mockOnSendMessage}
      />
    );

    const actionBtn = screen.getByText("Investigate the area");
    await userEvent.click(actionBtn);

    expect(mockOnSendMessage).toHaveBeenCalledWith("Investigate the area");
  });

  it("falls back to onSendMessage when onSuggestedAction is not provided", async () => {
    const actions = ["Look around"];
    render(<ChatBox {...defaultProps} suggestedActions={actions} />);

    const actionBtn = screen.getByText("Look around");
    await userEvent.click(actionBtn);

    expect(mockOnSendMessage).toHaveBeenCalledWith("Look around");
  });

  it("disables suggested action buttons when loading", () => {
    const actions = ["Explore the dungeon"];
    render(
      <ChatBox
        {...defaultProps}
        isLoading={true}
        suggestedActions={actions}
        onSuggestedAction={mockOnSendMessage}
      />
    );

    const actionButtons = screen.getAllByTestId("suggested-action-btn");
    for (const btn of actionButtons) {
      expect(btn).toBeDisabled();
    }
  });

  it("renders the help button", () => {
    render(<ChatBox {...defaultProps} />);
    expect(screen.getByTestId("help-btn")).toBeInTheDocument();
  });

  it("sends 'What can I do?' when help button is clicked", async () => {
    render(<ChatBox {...defaultProps} />);

    const helpBtn = screen.getByTestId("help-btn");
    await userEvent.click(helpBtn);

    expect(mockOnSendMessage).toHaveBeenCalledWith("What can I do?");
  });

  it("disables help button when loading", () => {
    render(<ChatBox {...defaultProps} isLoading={true} />);
    expect(screen.getByTestId("help-btn")).toBeDisabled();
  });
});
