import { PuzzleIcon } from '../components/Icon';

export function PluginRow({ plugin }) {
  return (
    <div className="name-line">
      <span className="plugin-name">{plugin.name}</span>
      <span className="status-icon" role="img" aria-label="需要对应插件才能读取" data-tip="需要对应插件才能读取" style={{ width: 18, height: 18, color: 'var(--state-info)' }}>
        <PuzzleIcon aria-hidden="true" />
      </span>
      <button type="button" className="icon-btn has-count" aria-label="补齐全部" data-tip="补齐全部" style={{ minWidth: 36, minHeight: 36 }}>
        <PuzzleIcon aria-hidden="true" />
        <span className="icon-btn-count">17</span>
      </button>
    </div>
  );
}