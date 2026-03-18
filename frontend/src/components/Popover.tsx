import { useEffect, useRef, useState } from "react";

type PopoverProps = {
  open?: boolean; // opcional: modo controlado
  onOpenChange?: (v: boolean) => void;
  placement?: "bottom-start" | "bottom-end" | "top-start" | "top-end";
  trigger: (props: {
    onClick: () => void;
    "aria-expanded": boolean;
    ref: (el: HTMLButtonElement | null) => void;
  }) => React.ReactNode;
  children: React.ReactNode;
  className?: string;
};

export default function Popover({
  open: controlledOpen,
  onOpenChange,
  placement = "bottom-start",
  trigger,
  children,
  className,
}: PopoverProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = useState(false);
  const isControlled = typeof controlledOpen === "boolean";
  const open = isControlled ? controlledOpen : uncontrolledOpen;

  const rootRef = useRef<HTMLDivElement | null>(null);
  const triggerElRef = useRef<HTMLButtonElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);

  const setOpen = (v: boolean) => {
    if (isControlled) onOpenChange?.(v);
    else setUncontrolledOpen(v);
  };

  // Cerrar con Escape
  useEffect(() => {
    function onEsc(e: KeyboardEvent) {
      if (!open) return;
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("keydown", onEsc);
    };
  }, [open]);

  // Cerrar al hacer clic fuera
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!open) return;
      const target = e.target as Node;
      const root = rootRef.current;
      if (root && !root.contains(target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
    };
  }, [open]);

  // Foco al panel al abrir
  useEffect(() => {
    if (open && panelRef.current) {
      panelRef.current.focus();
    }
  }, [open]);

  const setTriggerRef = (el: HTMLButtonElement | null) => {
    triggerElRef.current = el;
  };

  return (
    <div
      className={`popover-root ${className ?? ""}`}
      ref={rootRef}
      style={{ position: "relative", display: "inline-block" }}
    >
      {trigger({
        onClick: () => setOpen(!open),
        "aria-expanded": open,
        ref: setTriggerRef,
      })}
      {open && (
        <div
          className={`popover-panel ${placement}`}
          ref={panelRef}
          tabIndex={-1}
          role="dialog"
          aria-modal="false"
        >
          {children}
        </div>
      )}
    </div>
  );
}