import { useEffect, useState } from "react";

export function LoadingState({ label = "Loading…" }) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setSlow(true), 4000);
    return () => clearTimeout(t);
  }, []);
  return (
    <div className="state" role="status">
      <div className="spinner" />
      <p>{label}</p>
      {slow && (
        <p className="muted">
          Waking up the server. This can take up to a minute on the free plan.
        </p>
      )}
    </div>
  );
}

export function ErrorState({ title = "Couldn’t load tasks", message = "Please try again.", onRetry }) {
  return (
    <div className="state" role="alert">
      <div className="emoji">⚠️</div>
      <h2>{title}</h2>
      <p className="muted">{message}</p>
      <button className="btn btn-primary" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}

export function EmptyState({ filtered }) {
  return (
    <div className="state">
      <div className="emoji">📝</div>
      {filtered ? (
        <>
          <h2>No matching tasks</h2>
          <p className="muted">Try a different search or filter.</p>
        </>
      ) : (
        <>
          <h2>No tasks yet</h2>
          <p className="muted">Tap + to add your first task.</p>
        </>
      )}
    </div>
  );
}