import type React from "react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import styles from "./VisualActionButton.module.css";

interface VisualActionButtonProps {
  label: string;
  loading: boolean;
  onClick: () => void | Promise<void>;
  disabled: boolean;
  disabledReason?: string | null;
  testId: string;
  variant?: "default" | "secondary";
  style?: React.CSSProperties;
}

/**
 * Tooltip-wrapped visual-generation button, shared between the desktop
 * GameInterface layout and MobileGameLayout (both need to disable the
 * button with an explanatory tooltip when generation is unavailable).
 * Callers must render this inside a <TooltipProvider>.
 */
const VisualActionButton: React.FC<VisualActionButtonProps> = ({
  label,
  loading,
  onClick,
  disabled,
  disabledReason,
  testId,
  variant = "secondary",
  style,
}) => {
  const button = (
    <Button
      variant={variant}
      onClick={() => {
        void onClick();
      }}
      disabled={disabled}
      style={style}
      data-testid={testId}
    >
      {loading ? "Generating..." : label}
    </Button>
  );

  if (!disabled || !disabledReason) {
    return button;
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        {/* biome-ignore lint/a11y/noNoninteractiveTabindex: span is the focusable Radix Tooltip trigger for a disabled button */}
        <span className={styles.visualButtonWrapper} tabIndex={0}>
          {button}
        </span>
      </TooltipTrigger>
      <TooltipContent>{disabledReason}</TooltipContent>
    </Tooltip>
  );
};

export default VisualActionButton;
