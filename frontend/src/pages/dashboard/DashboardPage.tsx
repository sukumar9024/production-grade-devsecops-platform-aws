import { useAuth } from "../../hooks/useAuth";


export function DashboardPage() {
  const { user } = useAuth();

  return (
    <section>
      <h1>Dashboard</h1>

      <p>
        Welcome,{" "}
        {user?.full_name
          ?? user?.username}
      </p>

      <p>
        Role: {user?.role.name}
      </p>
    </section>
  );
}