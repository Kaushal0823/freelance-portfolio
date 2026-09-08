import React, { useState, useEffect, useCallback } from "react";
import { Plus, Trash2, Check, Circle, Loader2, GripVertical } from "lucide-react";

// ---------------------------------------------------------------------------
// TaskBoard — a small "full stack" style app.
// The React UI on top talks to window.storage as if it were a backend API:
// every create/update/delete does an async call and persists across reloads,
// which is the same shape as calling a real REST backend from a frontend.
// ---------------------------------------------------------------------------

const STORAGE_KEY = "taskboard:tasks";
const COLUMNS = [
  { id: "todo", label: "To do" },
  { id: "doing", label: "In progress" },
  { id: "done", label: "Done" },
];

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

export default function TaskBoard() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState("");
  const [dragId, setDragId] = useState(null);
  const [error, setError] = useState(null);

  // ---- "API layer" -------------------------------------------------------
  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await window.storage.get(STORAGE_KEY, false);
      const parsed = result ? JSON.parse(result.value) : [];
      setTasks(parsed);
    } catch (e) {
      // key not found on first run — start empty, not an error state
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const persist = useCallback(async (next) => {
    setSaving(true);
    try {
      const result = await window.storage.set(STORAGE_KEY, JSON.stringify(next), false);
      if (!result) throw new Error("Save failed");
    } catch (e) {
      setError("Couldn't save — your last change may not persist.");
    } finally {
      setSaving(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // ---- Task operations -----------------------------------------------------
  const addTask = async () => {
    const title = draft.trim();
    if (!title) return;
    const next = [...tasks, { id: uid(), title, status: "todo", createdAt: Date.now() }];
    setTasks(next);
    setDraft("");
    await persist(next);
  };

  const moveTask = async (id, status) => {
    const next = tasks.map((t) => (t.id === id ? { ...t, status } : t));
    setTasks(next);
    await persist(next);
  };

  const deleteTask = async (id) => {
    const next = tasks.filter((t) => t.id !== id);
    setTasks(next);
    await persist(next);
  };

  // ---- Drag and drop -----------------------------------------------------
  const onDrop = (columnId) => {
    if (dragId) moveTask(dragId, columnId);
    setDragId(null);
  };

  const counts = COLUMNS.reduce((acc, c) => {
    acc[c.id] = tasks.filter((t) => t.status === c.id).length;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-stone-100 p-6 md:p-10">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-stone-900">Task Board</h1>
            <p className="text-sm text-stone-500 mt-1">
              Backed by persistent storage — refresh the page, your tasks stay.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-stone-400 h-5">
            {saving && (
              <>
                <Loader2 size={14} className="animate-spin" /> Saving…
              </>
            )}
          </div>
        </header>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2">
            {error}
          </div>
        )}

        <div className="flex gap-2 mb-8">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTask()}
            placeholder="Add a task and press Enter…"
            className="flex-1 rounded-md border border-stone-300 bg-white px-4 py-2.5 text-sm text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-800"
          />
          <button
            onClick={addTask}
            className="rounded-md bg-stone-900 text-white px-4 py-2.5 text-sm font-medium flex items-center gap-1.5 hover:bg-stone-700 transition-colors"
          >
            <Plus size={16} /> Add
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24 text-stone-400 gap-2">
            <Loader2 className="animate-spin" size={18} /> Loading tasks…
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {COLUMNS.map((col) => (
              <div
                key={col.id}
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => onDrop(col.id)}
                className="bg-white rounded-lg border border-stone-200 p-4 min-h-[320px]"
              >
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold text-stone-700">{col.label}</h2>
                  <span className="text-xs text-stone-400 bg-stone-100 rounded-full px-2 py-0.5">
                    {counts[col.id]}
                  </span>
                </div>

                <div className="space-y-2">
                  {tasks
                    .filter((t) => t.status === col.id)
                    .map((t) => (
                      <div
                        key={t.id}
                        draggable
                        onDragStart={() => setDragId(t.id)}
                        className="group flex items-start gap-2 rounded-md border border-stone-200 bg-stone-50 px-3 py-2.5 cursor-grab active:cursor-grabbing"
                      >
                        <GripVertical size={14} className="text-stone-300 mt-0.5 shrink-0" />
                        <span className="flex-1 text-sm text-stone-800 break-words">{t.title}</span>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          {col.id !== "done" && (
                            <button
                              title="Mark done"
                              onClick={() =>
                                moveTask(t.id, col.id === "todo" ? "doing" : "done")
                              }
                              className="text-stone-400 hover:text-emerald-600"
                            >
                              {col.id === "todo" ? <Circle size={14} /> : <Check size={14} />}
                            </button>
                          )}
                          <button
                            title="Delete"
                            onClick={() => deleteTask(t.id)}
                            className="text-stone-400 hover:text-red-600"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  {counts[col.id] === 0 && (
                    <p className="text-xs text-stone-300 italic py-6 text-center">
                      Drop tasks here
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
