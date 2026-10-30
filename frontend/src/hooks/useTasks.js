import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client";

const EMPTY_COUNTS = { total: 0, pending: 0, completed: 0 };

export default function useTasks() {
  const [filters, setFilters] = useState({ status: "all", search: "", sort: "due_date" });
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [tasks, setTasks] = useState([]);
  const [counts, setCounts] = useState(EMPTY_COUNTS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const requestId = useRef(0);

  // Wait 300 ms after typing stops before searching
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(filters.search), 300);
    return () => clearTimeout(t);
  }, [filters.search]);

  const load = useCallback(
    async ({ silent = false } = {}) => {
      const id = ++requestId.current; // newest request wins
      if (!silent) {
        setLoading(true);
        setError("");
      }
      const params = new URLSearchParams({ status: filters.status, sort: filters.sort });
      if (debouncedSearch.trim()) params.set("search", debouncedSearch.trim());
      try {
        const data = await api(`/api/tasks?${params}`);
        if (id !== requestId.current) return;
        setTasks(data.tasks);
        setCounts(data.counts);
        setError("");
      } catch (err) {
        if (id !== requestId.current) return;
        if (silent) setNotice(err.message);
        else setError(err.message);
      } finally {
        if (id === requestId.current) setLoading(false);
      }
    },
    [filters.status, filters.sort, debouncedSearch]
  );

  useEffect(() => {
    load();
  }, [load]);

  // Checkbox: update the screen and counts immediately, then confirm with the server
  async function toggle(task) {
    const next = !task.is_completed;
    setTasks((ts) => ts.map((t) => (t.id === task.id ? { ...t, is_completed: next } : t)));
    setCounts((c) => ({
      ...c,
      pending: c.pending + (next ? -1 : 1),
      completed: c.completed + (next ? 1 : -1),
    }));
    try {
      await api(`/api/tasks/${task.id}`, { method: "PUT", body: { is_completed: next } });
    } catch (err) {
      setNotice(err.message || "Couldn’t update the task");
    }
    load({ silent: true }); // reconcile (also rolls back if the call failed)
  }

  async function saveTask(values, id) {
    await api(id ? `/api/tasks/${id}` : "/api/tasks", {
      method: id ? "PUT" : "POST",
      body: values,
    });
    await load({ silent: true });
  }

  async function removeTask(id) {
    await api(`/api/tasks/${id}`, { method: "DELETE" });
    await load({ silent: true });
  }

  return {
    filters,
    setFilters,
    tasks,
    counts,
    loading,
    error,
    notice,
    setNotice,
    reload: () => load(),
    toggle,
    saveTask,
    removeTask,
  };
}