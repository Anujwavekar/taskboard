import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ErrorState, LoadingState } from "../components/States";

export default function ProtectedRoute({ children }) {
  const { status, retry } = useAuth();
  if (status === "loading") return <LoadingState label="Checking your session…" />;
  if (status === "error")
    return (
      <ErrorState
        title="Couldn’t reach the server"
        message="Please check your connection and try again."
        onRetry={retry}
      />
    );
  if (status === "guest") return <Navigate to="/login" replace />;
  return children;
}