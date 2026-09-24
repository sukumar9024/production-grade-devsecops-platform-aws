import {
  Navigate,
  Outlet,
} from "react-router-dom";

import { useAuth } from "../hooks/useAuth";


export function ProtectedRoute() {
  const {
    authenticated,
    loading,
  } = useAuth();


  if (loading) {
    return (
      <div>
        Loading...
      </div>
    );
  }


  if (!authenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  return <Outlet />;
}