import { useState } from 'react';
import { Plus, Trash2, Link } from 'lucide-react';

export default function Settings() {
  const [boards, setBoards] = useState([]);
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');

  const addBoard = () => {
    if (!title || !url) return;
    const newBoard = { id: Date.now(), title, url };
    setBoards([...boards, newBoard]);
    // API placeholder
    fetch('/api/settings/boards', {
      method: 'POST',
      body: JSON.stringify(newBoard)
    });
    setTitle('');
    setUrl('');
  };

  const ignoreBoard = (id) => {
    setBoards(boards.filter(b => b.id !== id));
    // API placeholder
    fetch(`/api/settings/boards/${id}`, { method: 'DELETE' });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6 text-white">Job Board Settings</h1>

      <div className="bg-slate-800 rounded-lg shadow-xl border border-slate-700 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 text-white">Add Job Board</h2>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Board name (e.g., Indeed)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400"
          />
          <input
            type="url"
            placeholder="https://..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400"
          />
          <button
            onClick={addBoard}
            className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 transition-colors cursor-pointer"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {boards.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No job boards added yet.</p>
        ) : (
          boards.map(board => (
            <div key={board.id} className="bg-slate-800 rounded-lg shadow-xl border border-slate-700 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Link className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="font-medium text-white">{board.title}</p>
                  <p className="text-sm text-blue-400 hover:text-blue-300">{board.url}</p>
                </div>
              </div>
              <button
                onClick={() => ignoreBoard(board.id)}
                className="text-red-400 hover:text-red-300 transition-colors cursor-pointer"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}