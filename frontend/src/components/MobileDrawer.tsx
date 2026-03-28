import * as Dialog from "@radix-ui/react-dialog";
import type React from "react";
import styles from "./MobileDrawer.module.css";

interface MobileDrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  side?: "left" | "right";
  children: React.ReactNode;
}

const MobileDrawer: React.FC<MobileDrawerProps> = ({
  open,
  onClose,
  title,
  side = "left",
  children,
}) => {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className={styles.overlay} />
        <Dialog.Content
          className={`${styles.drawer} ${side === "right" ? styles.drawerRight : ""}`}
          aria-label={title}
          aria-describedby={undefined}
        >
          <div className={styles.drawerHeader}>
            <Dialog.Title className={styles.drawerTitle}>{title}</Dialog.Title>
            <Dialog.Close asChild>
              <button
                type="button"
                className={styles.closeButton}
                aria-label="Close"
              >
                &times;
              </button>
            </Dialog.Close>
          </div>
          <div className={styles.drawerContent}>{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};

export default MobileDrawer;
