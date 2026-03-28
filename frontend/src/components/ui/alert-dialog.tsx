import * as AlertDialogPrimitive from "@radix-ui/react-alert-dialog";
import type React from "react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const AlertDialog = AlertDialogPrimitive.Root;
const AlertDialogTrigger = AlertDialogPrimitive.Trigger;
const AlertDialogPortal = AlertDialogPrimitive.Portal;

const AlertDialogOverlay: React.FC<
  React.ComponentPropsWithRef<typeof AlertDialogPrimitive.Overlay>
> = ({ className, ...props }) => (
  <AlertDialogPrimitive.Overlay
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
);
AlertDialogOverlay.displayName = AlertDialogPrimitive.Overlay.displayName;

const AlertDialogContent: React.FC<
  React.ComponentPropsWithRef<typeof AlertDialogPrimitive.Content>
> = ({ className, ...props }) => (
  <AlertDialogPortal>
    <AlertDialogOverlay />
    <AlertDialogPrimitive.Content
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border border-border bg-card p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] rounded-lg",
        className
      )}
      {...props}
    />
  </AlertDialogPortal>
);
AlertDialogContent.displayName = AlertDialogPrimitive.Content.displayName;

const AlertDialogHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn(
      "flex flex-col space-y-2 text-center sm:text-left",
      className
    )}
    {...props}
  />
);
AlertDialogHeader.displayName = "AlertDialogHeader";

const AlertDialogFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
);
AlertDialogFooter.displayName = "AlertDialogFooter";

const AlertDialogTitle: React.FC<
  React.ComponentPropsWithRef<typeof AlertDialogPrimitive.Title>
> = ({ className, ...props }) => (
  <AlertDialogPrimitive.Title
    className={cn("text-lg font-semibold", className)}
    {...props}
  />
);
AlertDialogTitle.displayName = AlertDialogPrimitive.Title.displayName;

const AlertDialogDescription: React.FC<
  React.ComponentPropsWithRef<typeof AlertDialogPrimitive.Description>
> = ({ className, ...props }) => (
  <AlertDialogPrimitive.Description
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
);
AlertDialogDescription.displayName =
  AlertDialogPrimitive.Description.displayName;

const AlertDialogAction: React.FC<
  React.ComponentPropsWithRef<typeof AlertDialogPrimitive.Action>
> = ({ className, ...props }) => (
  <AlertDialogPrimitive.Action
    className={cn(buttonVariants(), className)}
    {...props}
  />
);
AlertDialogAction.displayName = AlertDialogPrimitive.Action.displayName;

const AlertDialogCancel: React.FC<
  React.ComponentPropsWithRef<typeof AlertDialogPrimitive.Cancel>
> = ({ className, ...props }) => (
  <AlertDialogPrimitive.Cancel
    className={cn(
      buttonVariants({ variant: "outline" }),
      "mt-2 sm:mt-0",
      className
    )}
    {...props}
  />
);
AlertDialogCancel.displayName = AlertDialogPrimitive.Cancel.displayName;

export {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  AlertDialogPortal,
  AlertDialogTitle,
  AlertDialogTrigger,
};
