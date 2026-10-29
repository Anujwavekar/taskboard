import { useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/api/health`)
      .then((r) => r.text())
      .then(setStatus)
      .catch(() => setStatus("API unreachable"));
  }, []);

  return <h1>TaskBoard API status: {status}</h1>;
}