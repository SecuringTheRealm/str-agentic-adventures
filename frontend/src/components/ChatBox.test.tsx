import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
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
			screen.getByPlaceholderText("What do you want to do?"),
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
			"I want to explore the castle",
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
		expect(document.querySelector(`.${styles.typingIndicator}`)).toBeInTheDocument();
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

		const dmMessage = screen.getByText("DM message").closest(`.${styles.message}`);
		const playerMessage = screen
			.getByText("Player message")
			.closest(`.${styles.message}`);

		expect(dmMessage).toHaveClass(styles.dmMessage);
		expect(playerMessage).toHaveClass(styles.playerMessage);
	});
});
