from .resource_module import ResourceModule
from .integrity_module import IntegrityModule
from .enviroment_module import EnvironmentModule

MODULE_REGISTRY = {
    "resources": ResourceModule,
    "integrity": IntegrityModule,
    "environment": EnvironmentModule
}