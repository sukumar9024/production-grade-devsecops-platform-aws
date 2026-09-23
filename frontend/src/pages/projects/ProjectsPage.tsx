import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import { useAuth } from "../../hooks/useAuth";

import { projectService } from "../../services/projectService";

import type {
  Project,
} from "../../types/project";

import { getApiErrorMessage } from "../../utils/apiError";


export function ProjectsPage() {
  const { user } = useAuth();

  const [
    projects,
    setProjects,
  ] = useState<Project[]>([]);

  const [
    name,
    setName,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);
  const [
    editingProject,
    setEditingProject,
    ] = useState<Project | null>(
    null
    )
  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  const canModify =
    user?.role.name === "Admin"
    || user?.role.name === "Engineer";

  const canDelete =
    user?.role.name === "Admin";


  async function loadProjects() {
    try {
      setError(null);

      const data =
        await projectService.list();

      setProjects(data);

    } catch (err) {
      setError(
        getApiErrorMessage(err)
      );

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void loadProjects();
  }, []);


  async function handleCreate(
    event: FormEvent
  ) {
    event.preventDefault();

    if (!canModify) {
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      await projectService.create({
        name,
        description:
          description || null,
      });

      setName("");
      setDescription("");

      await loadProjects();

    } catch (err) {
      setError(
        getApiErrorMessage(err)
      );

    } finally {
      setSubmitting(false);
    }
  }

  function beginEdit(
    project: Project
    ) {
    setEditingProject(project);

    setName(project.name);

    setDescription(
        project.description ?? ""
    );
    }

    if (editingProject) {
  await projectService.update(
    editingProject.id,
    {
      name,
      description:
        description || null,
    }
  );
} else {
  await projectService.create({
    name,
    description:
      description || null,
  });
}

  async function handleDelete(
    project: Project
  ) {
    if (!canDelete) {
      return;
    }

    const confirmed =
      window.confirm(
        `Delete project "${project.name}"?`
      );

    if (!confirmed) {
      return;
    }

    try {
      await projectService.remove(
        project.id
      );

      await loadProjects();

    } catch (err) {
      setError(
        getApiErrorMessage(err)
      );
    }
  }


  return (
    <section>
      <div className="page-header">
        <div>
          <h1>Projects</h1>

          <p>
            Manage SecureOps projects.
          </p>
        </div>
      </div>

      {error && (
        <div
          className="error-message"
          role="alert"
        >
          {error}
        </div>
      )}

      {canModify && (
        <section className="card">
          <h2>Create Project</h2>

          <form
            onSubmit={handleCreate}
            className="form-grid"
          >
            <div>
              <label htmlFor="project-name">
                Project name
              </label>

              <input
                id="project-name"
                value={name}
                minLength={3}
                maxLength={150}
                onChange={(event) =>
                  setName(
                    event.target.value
                  )
                }
                required
              />
            </div>

            <div>
              <label
                htmlFor="project-description"
              >
                Description
              </label>

              <textarea
                id="project-description"
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value
                  )
                }
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
            >
              {submitting
                ? "Creating..."
                : "Create Project"}
            </button>
          </form>
        </section>
      )}

      <section className="card">
        <h2>Projects</h2>

        {loading ? (
          <p>
            Loading projects...
          </p>
        ) : projects.length === 0 ? (
          <p>
            No projects found.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Created By</th>
                <th>Created</th>

                {canDelete && (
                  <th>Actions</th>
                )}
              </tr>
            </thead>

            <tbody>
              {projects.map(
                (project) => (
                  <tr
                    key={project.id}
                  >
                    <td>
                      {project.name}
                    </td>

                    <td>
                      {project.description
                        ?? "—"}
                    </td>

                    <td>
                      {
                        project
                          .created_by
                          .username
                      }
                    </td>

                    <td>
                      {
                        new Date(
                          project.created_at
                        ).toLocaleString()
                      }
                    </td>

                    {canDelete && (
                      <td>
                        <button
                          type="button"
                          onClick={() =>
                            void handleDelete(
                              project
                            )
                          }
                        >
                          Delete
                        </button>
                      </td>
                    )}
                  </tr>
                )
              )}
            </tbody>
          </table>
        )}
      </section>
    </section>
  );
}