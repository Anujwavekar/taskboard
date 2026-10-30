import { formatDate, isOverdue } from "../utils/date";

const LABEL = { low: "Low", medium: "Medium", high: "High" };

export default function TaskItem({ task, onToggle, onEdit, onDelete }) {
  const overdue = isOverdue(task.due_date, task.is_completed);
  return (
    <li className={`task ${task.is_completed ? "done" : ""}`}>
      <label className="check-wrap">
        <input
          type="checkbox"
          className="check"
          checked={task.is_completed}
          onChange={() => onToggle(task)}
          aria-label={`Mark "${task.title}" as ${task.is_completed ? "pending" : "done"}`}
        />
      </label>
      <div className="task-body">
        <div className="task-title">{task.title}</div>
        {task.description && <div className="task-desc">{task.description}</div>}
        <div className="task-meta">
          {task.is_completed ? (
            <span className="muted">✓ Completed</span>
          ) : (
            task.due_date && (
              <span className={overdue ? "due overdue" : "due"}>
                {overdue ? "Overdue · " : "Due "}
                {formatDate(task.due_date)}
              </span>
            )
          )}
          <span className={`priority ${task.priority}`}>{LABEL[task.priority]}</span>
        </div>
      </div>
      <div className="task-actions">
        <button className="icon-btn" aria-label="Edit task" onClick={() => onEdit(task)}>
          ✎
        </button>
        <button className="icon-btn" aria-label="Delete task" onClick={() => onDelete(task)}>
          🗑
        </button>
      </div>
    </li>
  );
}