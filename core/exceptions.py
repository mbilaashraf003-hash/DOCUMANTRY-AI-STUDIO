class ProjectError(Exception):
    """Base exception for project related errors."""
    pass

class ProjectNotFoundError(ProjectError):
    pass

class InvalidProjectError(ProjectError):
    pass

class CorruptedProjectFileError(ProjectError):
    pass

class ProjectPermissionError(ProjectError):
    pass
