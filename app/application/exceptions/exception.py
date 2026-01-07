# SCRIPT APPLICATION EXCEPTIONS


class ApplicationError(Exception):
    """Base application exception"""


class ScriptValidationError(ApplicationError):
    pass


class ScriptAlreadyExistsError(ApplicationError):
    pass


class ScriptCreationError(ApplicationError):
    pass


class ScriptNotFoundError(ApplicationError):
    pass


class ScriptPersistenceError(ApplicationError):
    pass


class ScriptProcessingDispatchError(ApplicationError):
    pass


# GENERATED SCRIPT ERRORS

class GeneratedScriptError(Exception):
    """Base exception for generated script use cases"""


class GeneratedScriptValidationError(GeneratedScriptError):
    pass


class GeneratedScriptPersistenceError(GeneratedScriptError):
    pass


class GeneratedScriptError(Exception):
    """Base exception for generated script use cases"""


class GeneratedScriptValidationError(GeneratedScriptError):
    pass


class GeneratedScriptPersistenceError(GeneratedScriptError):
    pass


class GeneratedScriptNotFoundError(GeneratedScriptError):
    pass