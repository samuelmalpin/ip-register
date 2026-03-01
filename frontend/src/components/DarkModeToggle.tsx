export function DarkModeToggle({ dark, onToggle }: { dark: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      className="rounded-md border border-slate-300 px-3 py-1 text-sm dark:border-slate-700"
    >
      {dark ? 'Light' : 'Dark'} mode
    </button>
  )
}
