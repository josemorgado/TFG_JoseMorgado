// src/components/MultiSelectNative.tsx
import { useMemo } from "react";

export type MultiSelectOption<V extends string | number = string> = {
  value: V;
  label: string;
};

type MultiSelectProps<V extends string | number = string> = {
  value: V[];
  options: MultiSelectOption<V>[];
  placeholder?: string; // no real placeholder en multiple, se ignora visualmente
  onChange: (values: V[]) => void;
  disabled?: boolean;
  className?: string;
  size?: number; // alto del listbox. Por defecto 4-6.
};

export default function MultiSelect<V extends string | number = string>({
  value,
  options,
  onChange,
  disabled,
  className,
  size = 5,
}: MultiSelectProps<V>) {
  const selectedSet = useMemo(() => new Set(value), [value]);

  return (
    <select
      multiple
      disabled={disabled}
      className={`input ${className ?? ""}`}
      size={Math.max(2, Math.min(size, Math.max(2, options.length)))}
      value={value.map(String)} // <select> trabaja con strings
      onChange={(e) => {
        const selected: V[] = Array.from(e.currentTarget.selectedOptions).map(
          (opt) => (typeof value[0] === "number" ? (Number(opt.value) as V) : (opt.value as V))
        );
        onChange(selected);
      }}
    >
      {options.map((opt) => (
        <option
          key={String(opt.value)}
          value={String(opt.value)}
          aria-selected={selectedSet.has(opt.value)}
        >
          {opt.label}
        </option>
      ))}
    </select>
  );
}
