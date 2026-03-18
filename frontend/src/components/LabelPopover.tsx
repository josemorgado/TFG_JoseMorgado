import Popover from "./Popover";

type LabelPopoverProps = {
  label: string;
  children: React.ReactNode;
  disabled?: boolean;
  placement?: "bottom-start" | "bottom-end" | "top-start" | "top-end";
};

export default function LabelPopover({
  label,
  children,
  disabled,
  placement = "bottom-start",
}: LabelPopoverProps) {
  return (
    <Popover
      placement={placement}
      trigger={({ onClick, "aria-expanded": expanded, ref }) => (
        <button
          type="button"
          ref={ref}
          className="word-trigger"
          aria-haspopup="dialog"
          aria-expanded={expanded}
          onClick={onClick}
          disabled={disabled}
          title={label}
        >
          <span className="word-trigger__text">{label}</span>
          <span className="word-trigger__caret" aria-hidden />
        </button>
      )}
    >
      <div className="popover-content">
        {children}
      </div>
    </Popover>
  );
}