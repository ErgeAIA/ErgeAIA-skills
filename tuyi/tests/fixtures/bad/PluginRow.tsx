import { Bell } from 'lucide-react';
import { PuzzleIcon } from '../components/Icon';

export function PluginRow({ plugin }) {
  return (
    <div className="name-line">
      <span className="plugin-name">{plugin.name}</span>
      <span className="status-icon" style={{ width: 18, height: 18, border: '1px solid #E2DDD3', background: '#FBE8DD' }}>
        <PuzzleIcon />
      </span>
      <button className="icon-btn has-count" style={{ width: 24, height: 24 }}>
        <PuzzleIcon />
        <span className="count-inside">17</span>
      </button>
    </div>
  );
}