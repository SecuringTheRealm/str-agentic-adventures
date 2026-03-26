import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../types";
import styles from "./ChatBox.module.css";

interface ChatBoxProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  streamingMessage?: string;
  suggestedActions?: string[];
  onSuggestedAction?: (action: string) => void;
}

const ChatBox: React.FC<ChatBoxProps> = ({
  messages,
  onSendMessage,
  isLoading,
  streamingMessage,
  suggestedActions,
  onSuggestedAction,
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

  const handleActionClick = (action: string) => {
    if (!isLoading) {
      if (onSuggestedAction) {
        onSuggestedAction(action);
      } else {
        onSendMessage(action);
      }
    }
  };

  const handleHelpClick = () => {
    if (!isLoading) {
      onSendMessage("What can I do?");
    }
  };

  const hasSuggestedActions =
    suggestedActions && suggestedActions.length > 0;

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

      {hasSuggestedActions && (
        <div className={styles.suggestedActions} data-testid="suggested-actions">
          <span className={styles.suggestedActionsLabel}>Suggested actions:</span>
          <div className={styles.actionButtons}>
            {suggestedActions.map((action) => (
              <button
                key={action}
                type="button"
                className={styles.actionButton}
                onClick={() => handleActionClick(action)}
                disabled={isLoading}
                data-testid="suggested-action-btn"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      <form className={styles.inputForm} onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="What do you want to do?"
          disabled={isLoading}
          data-testid="chat-input"
        />
        <button type="submit" disabled={isLoading || !input.trim()} data-testid="chat-send-btn">
          Send
        </button>
        <button
          type="button"
          className={styles.helpButton}
          onClick={handleHelpClick}
          disabled={isLoading}
          data-testid="help-btn"
          title="What can I do?"
        >
          ?
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
