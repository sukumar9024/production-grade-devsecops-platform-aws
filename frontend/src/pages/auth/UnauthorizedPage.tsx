import {
  Link,
} from "react-router-dom";


export function UnauthorizedPage() {
  return (
    <main>
      <h1>403</h1>

      <h2>Unauthorized</h2>

      <p>
        You do not have permission
        to access this page.
      </p>

      <Link to="/">
        Return to dashboard
      </Link>
    </main>
  );
}