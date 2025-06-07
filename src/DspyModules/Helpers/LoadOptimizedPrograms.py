import os

from DspyModules.ErrorResolverModule import ErrorResolverModule
from DspyModules.QueryGeneratorModule import QueryGenerator


def load_optimized_error_resolver_program() -> ErrorResolverModule:
    """
    Load optimized programs from the 'OptimizedPrograms' directory.
    """
    loaded_program = ErrorResolverModule()
    loaded_program.load(path="C:\\PydanticAiReporting\\src\\optimized_programs\\error_resolver_model.pkl")

    return loaded_program


def load_optimized_query_generator_program() -> QueryGenerator:
    """
    Load optimized programs from the 'OptimizedPrograms' directory.
    """
    loaded_program = QueryGenerator()
    loaded_program.load(path="C:\\PydanticAiReporting\\src\\optimized_programs\\query_generation_module.pkl")

    return loaded_program