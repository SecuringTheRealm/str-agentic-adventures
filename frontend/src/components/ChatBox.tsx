import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatMessage } from "../types";
import styles from "./ChatBox.module.css";
import VoiceIndicator from "./VoiceIndicator";
import VoiceMicButton from "./VoiceMicButton";

interface ChatBoxProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  streamingMessage?: string;
  suggestedActions?: string[];
  onSuggestedAction?: (action: string) => void;
  // Voice props (all optional — voice is progressive enhancement)
  voiceEnabled?: boolean;
  isSpeaking?: boolean;
  isListening?: boolean;
  onMicPressStart?: () => void;
  onMicPressEnd?: () => void;
}

const ChatBox: React.FC<ChatBoxProps> = ({
  messages,
  onSendMessage,
  isLoading,
  streamingMessage,
  suggestedActions,
  onSuggestedAction,
  voiceEnabled,
  isSpeaking,
  isListening,
  onMicPressStart,
  onMicPressEnd,
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

  const hasSuggestedActions = suggestedActions && suggestedActions.length > 0;

  return (
    <div className={styles.chatBox}>
      {voiceEnabled && <VoiceIndicator isSpeaking={isSpeaking ?? false} />}
      <ScrollArea className={styles.messagesContainer}>
        <div role="log" aria-live="polite" aria-label="Chat messages">
          {messages.map((message, index) => (
            <div
              key={`${message.text}-${index}`}
              className={`${styles.message} ${message.sender === "player" ? styles.playerMessage : styles.dmMessage}`}
            >
              <div className={styles.messageSender}>
                {message.sender === "player" ? "You" : "Dungeon Master"}
              </div>
              <div className={styles.messageText}>
                {message.sender === "dm" ? (
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                ) : (
                  message.text
                )}
              </div>
            </div>
          ))}
          {streamingMessage && (
            <div className={`${styles.message} ${styles.dmMessage}`}>
              <div className={styles.messageSender}>Dungeon Master</div>
              <div className={`${styles.messageText} ${styles.streaming}`}>
                {streamingMessage ? (
                  <ReactMarkdown>{streamingMessage}</ReactMarkdown>
                ) : null}
                <span className={styles.streamingCursor}>|</span>
              </div>
            </div>
          )}
          {isLoading && !streamingMessage && (
            <div className={`${styles.message} ${styles.dmMessage}`}>
              <div className={styles.messageSender}>Dungeon Master</div>
              <output
                className={`${styles.messageText} ${styles.loading}`}
                aria-label="Loading"
              >
                <div className={styles.typingIndicator}>
                  <span />
                  <span />
                  <span />
                </div>
              </output>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {hasSuggestedActions && (
        <div
          className={styles.suggestedActions}
          data-testid="suggested-actions"
        >
          <span className={styles.suggestedActionsLabel}>
            Suggested actions:
          </span>
          <div className={styles.actionButtons}>
            {suggestedActions.map((action) => (
              <Button
                key={action}
                type="button"
                variant="secondary"
                size="sm"
                className={styles.actionButton}
                onClick={() => handleActionClick(action)}
                disabled={isLoading}
                data-testid="suggested-action-btn"
              >
                {action}
              </Button>
            ))}
          </div>
        </div>
      )}

      <form className={styles.inputForm} onSubmit={handleSubmit}>
        {voiceEnabled && onMicPressStart && onMicPressEnd && (
          <VoiceMicButton
            isListening={isListening ?? false}
            disabled={isLoading || (isSpeaking ?? false)}
            onPressStart={onMicPressStart}
            onPressEnd={onMicPressEnd}
          />
        )}
        <Input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="What do you want to do?"
          aria-label="Enter your action"
          disabled={isLoading}
          data-testid="chat-input"
        />
        <Button
          type="submit"
          disabled={isLoading || !input.trim()}
          data-testid="chat-send-btn"
        >
          Send
        </Button>
        <Button
          type="button"
          variant="outline"
          size="icon"
          className={styles.helpButton}
          onClick={handleHelpClick}
          disabled={isLoading}
          data-testid="help-btn"
          title="What can I do?"
        >
          ?
        </Button>
      </form>
    </div>
  );
};

export default ChatBox;
