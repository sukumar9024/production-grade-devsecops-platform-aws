import apiClient from "../api/client";

import type {
  Project,
  ProjectCreate,
  ProjectUpdate,
} from "../types/project";


export const projectService = {
  async list(): Promise<Project[]> {
    const response =
      await apiClient.get<Project[]>(
        "/api/v1/projects"
      );

    return response.data;
  },

  async create(
    payload: ProjectCreate
  ): Promise<Project> {
    const response =
      await apiClient.post<Project>(
        "/api/v1/projects",
        payload
      );

    return response.data;
  },

  async update(
    projectId: string,
    payload: ProjectUpdate
  ): Promise<Project> {
    const response =
      await apiClient.patch<Project>(
        `/api/v1/projects/${projectId}`,
        payload
      );

    return response.data;
  },

  async remove(
    projectId: string
  ): Promise<void> {
    await apiClient.delete(
      `/api/v1/projects/${projectId}`
    );
  },
};