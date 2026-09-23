import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.deployment import Deployment
from app.models.enums import DeploymentStatus


class DeploymentRepository:
    @staticmethod
    def get_by_id(
        db: Session,
        deployment_id: uuid.UUID,
    ) -> Deployment | None:
        statement = (
            select(Deployment)
            .options(
                joinedload(Deployment.service)
            )
            .where(
                Deployment.id == deployment_id
            )
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        offset: int,
        limit: int,
        service_id: uuid.UUID | None = None,
        status: DeploymentStatus | None = None,
    ) -> list[Deployment]:
        statement = (
            select(Deployment)
            .options(
                joinedload(Deployment.service)
            )
            .order_by(
                Deployment.created_at.desc()
            )
        )

        if service_id is not None:
            statement = statement.where(
                Deployment.service_id == service_id
            )

        if status is not None:
            statement = statement.where(
                Deployment.status == status
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
        deployment: Deployment,
    ) -> Deployment:
        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        return deployment

    @staticmethod
    def save(
        db: Session,
        deployment: Deployment,
    ) -> Deployment:
        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        return deployment