import { useState } from "react";
import type { FormEvent } from "react";
import { login } from "../lib/api";

interface LoginProps {
  onLogin: () => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login(username, password);
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-(--color-void) px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md p-8 rounded-xl border border-(--color-line) bg-(--color-steel) shadow-2xl"
      >
        <div className="flex items-center gap-3 mb-8">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2L3 6v6c0 5 3.8 8.7 9 10 5.2-1.3 9-5 9-10V6l-9-4z"
              stroke="#38E1C6"
              strokeWidth="1.6"
            />
            <path
              d="M8.5 12l2.3 2.3L15.5 9"
              stroke="#38E1C6"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          <div>
            <h1 className="text-xl text-(--color-bone) font-semibold">
              AegisAgent-AI
            </h1>
            <p className="text-xs text-(--color-mist)">
              Security Operations Console
            </p>
          </div>
        </div>

        <h2 className="text-lg text-(--color-bone) mb-5">
          Administrator Login
        </h2>

        <label className="block mb-4">
          <span className="block text-xs text-(--color-mist) mb-2">
            Username
          </span>

          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            className="w-full rounded-lg border border-(--color-line) bg-(--color-void) px-3 py-2.5 text-(--color-bone) outline-none focus:border-(--color-cyan)"
          />
        </label>

        <label className="block mb-5">
          <span className="block text-xs text-(--color-mist) mb-2">
            Password
          </span>

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            className="w-full rounded-lg border border-(--color-line) bg-(--color-void) px-3 py-2.5 text-(--color-bone) outline-none focus:border-(--color-cyan)"
          />
        </label>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !username || !password}
          className="w-full rounded-lg bg-(--color-cyan) px-4 py-2.5 font-semibold text-(--color-void) disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}
