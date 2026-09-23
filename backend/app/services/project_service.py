import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import (
    ProjectRepository,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectService:
    @staticmethod
    def create_project(
        db: Session,
        payload: ProjectCreate,
        current_user: User,
    ) -> Project:
        normalized_name = payload.name.strip()

        existing_project = (
            ProjectRepository.get_by_name(
                db=db,
                name=normalized_name,
            )
        )

        if existing_project is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A project with this name "
                    "already exists."
                ),
            )

        project = Project(
            name=normalized_name,
            description=(
                payload.description.strip()
                if payload.description
                else None
            ),
            created_by_id=current_user.id,
        )

        created_project = (
            ProjectRepository.create(
                db=db,
                project=project,
            )
        )

        return ProjectRepository.get_by_id(
            db=db,
            project_id=created_project.id,
        )

    @staticmethod
    def list_projects(
        db: Session,
        offset: int,
        limit: int,
    ) -> list[Project]:
        return ProjectRepository.get_all(
            db=db,
            offset=offset,
            limit=limit,
        )

    @staticmethod
    def get_project(
        db: Session,
        project_id: uuid.UUID,
    ) -> Project:
        project = ProjectRepository.get_by_id(
            db=db,
            project_id=project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        return project

    @staticmethod
    def update_project(
        db: Session,
        project_id: uuid.UUID,
        payload: ProjectUpdate,
    ) -> Project:
        project = ProjectService.get_project(
            db=db,
            project_id=project_id,
        )

        if payload.name is not None:
            normalized_name = (
                payload.name.strip()
            )

            existing_project = (
                ProjectRepository.get_by_name(
                    db=db,
                    name=normalized_name,
                )
            )

            if (
                existing_project is not None
                and existing_project.id
                != project.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A project with this name "
                        "already exists."
                    ),
                )

            project.name = normalized_name

        if payload.description is not None:
            project.description = (
                payload.description.strip()
                or None
            )

        ProjectRepository.save(
            db=db,
            project=project,
        )

        return ProjectRepository.get_by_id(
            db=db,
            project_id=project.id,
        )

    @staticmethod
    def delete_project(
        db: Session,
        project_id: uuid.UUID,
    ) -> None:
        project = ProjectService.get_project(
            db=db,
            project_id=project_id,
        )

        ProjectRepository.delete(
            db=db,
            project=project,
        )