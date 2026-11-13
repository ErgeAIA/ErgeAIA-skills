export function ActionRow({ phase, icon, onClick }: { phase: string; icon: string; onClick: () => void }) {
  return (
    <button
      type="button"
      className={`action-btn is-${phase}`}
      aria-label={phase === "sync" ? "处理中…" : "执行"}
      onClick={onClick}
    >
      <span className="action-slot">
        <Icon name={icon} className="action-ico ico-idle" />
        <Icon name="loader-circle" className="action-ico ico-sync" />
      </span>
    </button>
  );
}
