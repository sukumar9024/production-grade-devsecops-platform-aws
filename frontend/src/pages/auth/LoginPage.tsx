import {
  useState,
  type FormEvent,
} from "react";

import axios from "axios";

import {
  Navigate,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";


export function LoginPage() {
  const navigate = useNavigate();

  const {
    authenticated,
    login,
  } = useAuth();

  const [identity, setIdentity] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState<string | null>(null);

  const [submitting, setSubmitting] =
    useState(false);


  if (authenticated) {
    return (
      <Navigate
        to="/"
        replace
      />
    );
  }


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    setError(null);
    setSubmitting(true);

    try {
      await login({
        identity,
        password,
      });

      navigate("/");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(
          err.response?.data?.detail
          ?? "Unable to sign in."
        );
      } else {
        setError(
          "Unable to sign in."
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <main>
      <h1>SecureOps</h1>

      <h2>Sign in</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="identity">
            Email or username
          </label>

          <input
            id="identity"
            type="text"
            value={identity}
            onChange={(event) =>
              setIdentity(
                event.target.value
              )
            }
            required
          />
        </div>

        <div>
          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value
              )
            }
            required
          />
        </div>

        {error && (
          <p role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
        >
          {submitting
            ? "Signing in..."
            : "Sign in"}
        </button>
      </form>
    </main>
  );
}