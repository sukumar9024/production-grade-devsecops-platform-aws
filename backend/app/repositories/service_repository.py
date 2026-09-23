import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import Environment
from app.models.service import Service


class ServiceRepository:
    @staticmethod
    def get_by_id(
        db: Session,
        service_id: uuid.UUID,
    ) -> Service | None:
        statement = (
            select(Service)
            .options(
                joinedload(Service.project)
            )
            .where(
                Service.id == service_id
            )
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_identity(
        db: Session,
        project_id: uuid.UUID,
        name: str,
        environment: Environment,
    ) -> Service | None:
        statement = select(Service).where(
            Service.project_id == project_id,
            Service.name == name,
            Service.environment == environment,
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        offset: int,
        limit: int,
        project_id: uuid.UUID | None = None,
        environment: Environment | None = None,
    ) -> list[Service]:
        statement = (
            select(Service)
            .options(
                joinedload(Service.project)
            )
            .order_by(
                Service.created_at.desc()
            )
        )

        if project_id is not None:
            statement = statement.where(
                Service.project_id == project_id
            )

        if environment is not None:
            statement = statement.where(
                Service.environment == environment
            )

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def create(
        db: Session,
        service: Service,
    ) -> Service:
        db.add(service)
        db.commit()
        db.refresh(service)

        return service

    @staticmethod
    def save(
        db: Session,
        service: Service,
    ) -> Service:
        db.add(service)
        db.commit()
        db.refresh(service)

        return service

    @staticmethod
    def delete(
        db: Session,
        service: Service,
    ) -> None:
        db.delete(service)
        db.commit()