import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project


class ProjectRepository:
    @staticmethod
    def get_by_id(
        db: Session,
        project_id: uuid.UUID,
    ) -> Project | None:
        statement = (
            select(Project)
            .options(
                joinedload(Project.created_by)
            )
            .where(
                Project.id == project_id
            )
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Project | None:
        statement = select(Project).where(
            func.lower(Project.name)
            == name.lower()
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        offset: int,
        limit: int,
    ) -> list[Project]:
        statement = (
            select(Project)
            .options(
                joinedload(Project.created_by)
            )
            .order_by(
                Project.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def create(
        db: Session,
        project: Project,
    ) -> Project:
        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def save(
        db: Session,
        project: Project,
    ) -> Project:
        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete(
        db: Session,
        project: Project,
    ) -> None:
        db.delete(project)
        db.commit()