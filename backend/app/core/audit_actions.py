class AuditActions:
    USER_REGISTERED = "user.registered"

    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"

    USER_ROLE_CHANGED = "user.role.changed"
    USER_STATUS_CHANGED = "user.status.changed"

    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"

    SERVICE_CREATED = "service.created"
    SERVICE_UPDATED = "service.updated"
    SERVICE_DELETED = "service.deleted"

    DEPLOYMENT_CREATED = "deployment.created"
    DEPLOYMENT_UPDATED = "deployment.updated"

    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
