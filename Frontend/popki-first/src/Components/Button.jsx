export default function Button({ title, className, icon, disabled }) {
  return (
    <button
      disabled={disabled}
      className={`flex items-center justify-center gap-2 px-3.75 py-1 text-white border border-[var(--border-brand)] h-8 transition-colors duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed ${className || ""}`}
    >
      {title}
      {icon}
    </button>
  );
}