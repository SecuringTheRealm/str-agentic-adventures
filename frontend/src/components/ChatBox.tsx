import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import "./ChatBox.css";

interface ChatMessage {
	text: string;
	sender: "player" | "dm";
}

interface ChatBoxProps {
	messages: ChatMessage[];
	onSendMessage: (message: string) => void;
	isLoading: boolean;
}

const ChatBox: React.FC<ChatBoxProps> = ({
	messages,
	onSendMessage,
	isLoading,
}) => {
	const [input, setInput] = useState<string>("");
	const messagesEndRef = useRef<HTMLDivElement>(null);

	// Scroll to bottom when messages change
	const scrollToBottom = useCallback(() => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, []);

	useEffect(() => {
		if (messages.length) {
			scrollToBottom();
		}
	}, [messages, scrollToBottom]);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (input.trim() && !isLoading) {
			onSendMessage(input);
			setInput("");
		}
	};

	return (
		<div className="chat-box">
			<div className="messages-container">
				{messages.map((message, index) => (
					<div
						key={`${message.text}-${index}`}
						className={`message ${message.sender === "player" ? "player-message" : "dm-message"}`}
					>
						<div className="message-sender">
							{message.sender === "player" ? "You" : "Dungeon Master"}
						</div>
						<div className="message-text">{message.text}</div>
					</div>
				))}
				{isLoading && (
					<div className="message dm-message">
						<div className="message-sender">Dungeon Master</div>
						<div className="message-text loading">
							<div className="typing-indicator">
								<span />
								<span />
								<span />
							</div>
						</div>
					</div>
				)}
				<div ref={messagesEndRef} />
			</div>

			<form className="input-form" onSubmit={handleSubmit}>
				<input
					type="text"
					value={input}
					onChange={(e) => setInput(e.target.value)}
					placeholder="What do you want to do?"
					disabled={isLoading}
				/>
				<button type="submit" disabled={isLoading || !input.trim()}>
					Send
				</button>
			</form>
		</div>
	);
};

export default ChatBox;
