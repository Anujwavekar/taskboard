import { useEffect, useState } from "react";

// task = null → Add mode; task = object → Edit mode (pre-filled)
export default function TaskFormModal({ task, onClose, onSave }) {
  const [form, setForm] = useState({
    title: task?.title ?? "",
    description: task?.description ?? "",
    priority: task?.priority ?? "medium",
    due_date: task?.due_date ?? "",
  });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    setFormError("");
    if (!form.title.trim()) {
      setErrors({ title: "Title is required" });
      return;
    }
    setErrors({});
    setSaving(true);
    try {
      await onSave(
        {
          title: form.title.trim(),
          description: form.description.trim() || null,
          priority: form.priority,
          due_date: form.due_date || null,
        },
        task?.id
      );
      onClose();
    } catch (err) {
      const fieldErrors = err.errors || {};
      setErrors(fieldErrors);
      setFormError(Object.keys(fieldErrors).length ? "" : err.message);
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <form className="modal" onSubmit={submit} noValidate>
        <div className="modal-head">
          <h2>{task ? "Edit task" : "Add task"}</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="field">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            className={`input ${errors.title ? "invalid" : ""}`}
            value={form.title}
            onChange={set("title")}
            maxLength={150}
            autoFocus
          />
          {errors.title && <div className="error-text">{errors.title}</div>}
        </div>

        <div className="field">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            className="input"
            rows={3}
            placeholder="Add details (optional)"
            value={form.description}
            onChange={set("description")}
            maxLength={2000}
          />
          {errors.description && <div className="error-text">{errors.description}</div>}
        </div>

        <div className="field">
          <label htmlFor="priority">Priority</label>
          <select id="priority" className="input" value={form.priority} onChange={set("priority")}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="due">Due date</label>
          <input id="due" type="date" className="input" value={form.due_date} onChange={set("due_date")} />
          {errors.due_date && <div className="error-text">{errors.due_date}</div>}
        </div>

        {formError && <div className="error-text">{formError}</div>}

        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving…" : "Save task"}
          </button>
        </div>
      </form>
    </div>
  );
}