import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import Environment
from app.models.service import Service
from app.repositories.project_repository import ProjectRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
)


class ServiceService:
    @staticmethod
    def create_service(
        db: Session,
        payload: ServiceCreate,
    ) -> Service:
        project = ProjectRepository.get_by_id(
            db=db,
            project_id=payload.project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        normalized_name = payload.name.strip()

        existing_service = ServiceRepository.get_by_identity(
            db=db,
            project_id=payload.project_id,
            name=normalized_name,
            environment=payload.environment,
        )

        if existing_service is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A service with this name and "
                    "environment already exists "
                    "in the project."
                ),
            )

        service = Service(
            project_id=payload.project_id,
            name=normalized_name,
            environment=payload.environment,
            version=(payload.version.strip() if payload.version else None),
            health_check_url=(
                str(payload.health_check_url) if payload.health_check_url else None
            ),
        )

        created_service = ServiceRepository.create(
            db=db,
            service=service,
        )

        return ServiceRepository.get_by_id(
            db=db,
            service_id=created_service.id,
        )

    @staticmethod
    def list_services(
        db: Session,
        offset: int,
        limit: int,
        project_id: uuid.UUID | None,
        environment: Environment | None,
    ) -> list[Service]:
        return ServiceRepository.get_all(
            db=db,
            offset=offset,
            limit=limit,
            project_id=project_id,
            environment=environment,
        )

    @staticmethod
    def get_service(
        db: Session,
        service_id: uuid.UUID,
    ) -> Service:
        service = ServiceRepository.get_by_id(
            db=db,
            service_id=service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return service

    @staticmethod
    def update_service(
        db: Session,
        service_id: uuid.UUID,
        payload: ServiceUpdate,
    ) -> Service:
        service = ServiceService.get_service(
            db=db,
            service_id=service_id,
        )

        new_name = payload.name.strip() if payload.name is not None else service.name

        new_environment = (
            payload.environment
            if payload.environment is not None
            else service.environment
        )

        existing_service = ServiceRepository.get_by_identity(
            db=db,
            project_id=service.project_id,
            name=new_name,
            environment=new_environment,
        )

        if existing_service is not None and existing_service.id != service.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A service with this name and "
                    "environment already exists "
                    "in the project."
                ),
            )

        if payload.name is not None:
            service.name = new_name

        if payload.environment is not None:
            service.environment = payload.environment

        if payload.version is not None:
            service.version = payload.version.strip() or None

        if payload.status is not None:
            service.status = payload.status

        if payload.health_check_url is not None:
            service.health_check_url = str(payload.health_check_url)

        ServiceRepository.save(
            db=db,
            service=service,
        )

        return ServiceRepository.get_by_id(
            db=db,
            service_id=service.id,
        )

    @staticmethod
    def delete_service(
        db: Session,
        service_id: uuid.UUID,
    ) -> None:
        service = ServiceService.get_service(
            db=db,
            service_id=service_id,
        )

        ServiceRepository.delete(
            db=db,
            service=service,
        )
