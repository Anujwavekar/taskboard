import { useState } from "react";
import Header from "../components/Header";
import TaskItem from "../components/TaskItem";
import TaskFormModal from "../components/TaskFormModal";
import ConfirmDialog from "../components/ConfirmDialog";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import useTasks from "../hooks/useTasks";

const TABS = [
  ["all", "All", "All"],
  ["pending", "Pending", "Pending"],
  ["completed", "Completed", "Done"],
];

export default function TasksPage() {
  const t = useTasks();
  const [modal, setModal] = useState(null); // null | { task: null | task }
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const setFilter = (key, value) => t.setFilters((f) => ({ ...f, [key]: value }));

  async function confirmDelete() {
    setDeleting(true);
    try {
      await t.removeTask(toDelete.id);
    } catch (err) {
      t.setNotice(err.message);
    }
    setDeleting(false);
    setToDelete(null);
  }

  let content;
  if (t.error) {
    content = <ErrorState message="Please try again." onRetry={t.reload} />;
  } else if (t.loading && t.tasks.length === 0) {
    content = <LoadingState />;
  } else if (t.tasks.length === 0) {
    content = <EmptyState filtered={t.counts.total > 0} />;
  } else {
    content = (
      <ul className="task-list">
        {t.tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={t.toggle}
            onEdit={(x) => setModal({ task: x })}
            onDelete={setToDelete}
          />
        ))}
      </ul>
    );
  }

  return (
    <>
      <Header />
      <main className="container">
        <div className="page-title">
          <h1>My Tasks</h1>
          <button className="btn btn-primary add-desktop" onClick={() => setModal({ task: null })}>
            + Add task
          </button>
        </div>

        {t.notice && (
          <div className="notice" role="alert">
            <span>{t.notice}</span>
            <button className="icon-btn" onClick={() => t.setNotice("")} aria-label="Dismiss">
              ✕
            </button>
          </div>
        )}

        <section className="stats">
          <div className="stat"><div className="stat-value">{t.counts.total}</div><div className="stat-label">Total</div></div>
          <div className="stat"><div className="stat-value">{t.counts.pending}</div><div className="stat-label">Pending</div></div>
          <div className="stat"><div className="stat-value">{t.counts.completed}</div><div className="stat-label">Completed</div></div>
        </section>

        <section className="toolbar">
          <div className="tabs">
            {TABS.map(([key, long, short]) => (
              <button key={key} className={`tab ${t.filters.status === key ? "active" : ""}`} onClick={() => setFilter("status", key)}>
                <span className="long">{long}</span>
                <span className="short">{short}</span>
              </button>
            ))}
          </div>
          <input
            className="input search"
            type="search"
            placeholder="🔍 Search tasks…"
            value={t.filters.search}
            onChange={(e) => setFilter("search", e.target.value)}
          />
          <select className="input sort" value={t.filters.sort} onChange={(e) => setFilter("sort", e.target.value)} aria-label="Sort by">
            <option value="due_date">Sort: Due date</option>
            <option value="priority">Sort: Priority</option>
          </select>
        </section>

        {content}
      </main>

      <button className="fab" onClick={() => setModal({ task: null })} aria-label="Add task">
        +
      </button>

      {modal && (
        <TaskFormModal task={modal.task} onClose={() => setModal(null)} onSave={t.saveTask} />
      )}
      {toDelete && (
        <ConfirmDialog
          title="Delete task?"
          message={`Are you sure you want to delete “${toDelete.title}”? This can’t be undone.`}
          confirmLabel="Delete"
          busy={deleting}
          onConfirm={confirmDelete}
          onCancel={() => setToDelete(null)}
        />
      )}
    </>
  );
}