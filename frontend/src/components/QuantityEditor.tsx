import { useState } from "react";

type Props = {
  quantity?: number | null;
  onSave: (quantity: number | null) => Promise<void>;
};

export default function QuantityEditor({ quantity, onSave }: Props) {
  const [value, setValue] = useState(quantity?.toString() ?? "");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    try {
      const parsed = value.trim() === "" ? null : Number(value);
      await onSave(Number.isFinite(parsed as number) ? parsed : null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="quantity-editor">
      <input
        inputMode="decimal"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Qty"
        aria-label="Optional quantity"
      />
      <button disabled={busy} onClick={save}>Save</button>
    </div>
  );
}
