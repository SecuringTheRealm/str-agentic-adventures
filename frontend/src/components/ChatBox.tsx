import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./ChatBox.module.css";

interface ChatMessage {
  text: string;
  sender: "player" | "dm";
  isStreaming?: boolean;
}

interface ChatBoxProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  streamingMessage?: string;
}

const ChatBox: React.FC<ChatBoxProps> = ({
  messages,
  onSendMessage,
  isLoading,
  streamingMessage,
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
    <div className={styles.chatBox}>
      <div className={styles.messagesContainer}>
        {messages.map((message, index) => (
          <div
            key={`${message.text}-${index}`}
            className={`${styles.message} ${message.sender === "player" ? styles.playerMessage : styles.dmMessage}`}
          >
            <div className={styles.messageSender}>
              {message.sender === "player" ? "You" : "Dungeon Master"}
            </div>
            <div className={styles.messageText}>{message.text}</div>
          </div>
        ))}
        {streamingMessage && (
          <div className={`${styles.message} ${styles.dmMessage}`}>
            <div className={styles.messageSender}>Dungeon Master</div>
            <div className={`${styles.messageText} ${styles.streaming}`}>
              {streamingMessage}
              <span className={styles.streamingCursor}>|</span>
            </div>
          </div>
        )}
        {isLoading && !streamingMessage && (
          <div className={`${styles.message} ${styles.dmMessage}`}>
            <div className={styles.messageSender}>Dungeon Master</div>
            <div className={`${styles.messageText} ${styles.loading}`}>
              <div className={styles.typingIndicator}>
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className={styles.inputForm} onSubmit={handleSubmit}>
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
