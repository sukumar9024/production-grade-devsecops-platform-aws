import uuid
from datetime import UTC, datetime
from typing import ClassVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.models.enums import DeploymentStatus
from app.repositories.deployment_repository import (
    DeploymentRepository,
)
from app.repositories.service_repository import (
    ServiceRepository,
)
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
)


class DeploymentService:
    ALLOWED_TRANSITIONS: ClassVar[dict] = {
        DeploymentStatus.PENDING: {
            DeploymentStatus.IN_PROGRESS,
            DeploymentStatus.FAILED,
        },
        DeploymentStatus.IN_PROGRESS: {
            DeploymentStatus.SUCCESS,
            DeploymentStatus.FAILED,
        },
        DeploymentStatus.SUCCESS: {DeploymentStatus.ROLLED_BACK},
        DeploymentStatus.FAILED: {DeploymentStatus.ROLLED_BACK},
        DeploymentStatus.ROLLED_BACK: set(),
    }

    @staticmethod
    def create_deployment(
        db: Session,
        payload: DeploymentCreate,
    ) -> Deployment:
        service = ServiceRepository.get_by_id(
            db=db,
            service_id=payload.service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        deployment = Deployment(
            service_id=payload.service_id,
            version=payload.version.strip(),
            git_commit=payload.git_commit.strip(),
            image_digest=(
                payload.image_digest.strip() if payload.image_digest else None
            ),
            pipeline_id=(payload.pipeline_id.strip() if payload.pipeline_id else None),
            status=DeploymentStatus.PENDING,
        )

        created_deployment = DeploymentRepository.create(
            db=db,
            deployment=deployment,
        )

        return DeploymentRepository.get_by_id(
            db=db,
            deployment_id=created_deployment.id,
        )

    @staticmethod
    def list_deployments(
        db: Session,
        offset: int,
        limit: int,
        service_id: uuid.UUID | None,
        deployment_status: DeploymentStatus | None,
    ) -> list[Deployment]:
        return DeploymentRepository.get_all(
            db=db,
            offset=offset,
            limit=limit,
            service_id=service_id,
            status=deployment_status,
        )

    @staticmethod
    def get_deployment(
        db: Session,
        deployment_id: uuid.UUID,
    ) -> Deployment:
        deployment = DeploymentRepository.get_by_id(
            db=db,
            deployment_id=deployment_id,
        )

        if deployment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found.",
            )

        return deployment

    @staticmethod
    def update_deployment(
        db: Session,
        deployment_id: uuid.UUID,
        payload: DeploymentUpdate,
    ) -> Deployment:
        deployment = DeploymentService.get_deployment(
            db=db,
            deployment_id=deployment_id,
        )

        if payload.status is not None and payload.status != deployment.status:
            allowed = DeploymentService.ALLOWED_TRANSITIONS.get(
                deployment.status, set()
            )
            if payload.status not in allowed:
                raise HTTPException(
                    status_code=409, detail="Invalid deployment status transition."
                )
            if (
                payload.status == DeploymentStatus.FAILED
                and not (payload.failure_reason or "").strip()
            ):
                raise HTTPException(
                    status_code=422,
                    detail="failure_reason is required when deployment status is failed.",
                )
            deployment.status = payload.status
            if payload.status == DeploymentStatus.SUCCESS:
                deployment.failure_reason = None
                if deployment.deployed_at is None:
                    deployment.deployed_at = datetime.now(UTC)

        if payload.image_digest is not None:
            deployment.image_digest = payload.image_digest.strip() or None

        if payload.pipeline_id is not None:
            deployment.pipeline_id = payload.pipeline_id.strip() or None

        if payload.deployed_at is not None:
            deployment.deployed_at = payload.deployed_at

        if payload.failure_reason is not None:
            deployment.failure_reason = payload.failure_reason.strip() or None

        DeploymentRepository.save(
            db=db,
            deployment=deployment,
        )

        return DeploymentRepository.get_by_id(
            db=db,
            deployment_id=deployment.id,
        )
