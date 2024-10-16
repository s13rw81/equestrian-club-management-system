from fastapi import APIRouter, Depends
from role_based_access_control import RoleBasedAccessControl
from typing import Annotated
from models.user import UserInternal
from models.user.enums import UserRoles
from .role_based_parameter_control import DifferentRolesDifferentParameters

demo_rbac_router = APIRouter(
    prefix="/rbac-demo",
    tags=["rbac-demo"]
)


@demo_rbac_router.get("/only-for-admin")
def only_for_admin_get_route(
        user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.ADMIN}))
        ]):
    return {"message": "OK"}


@demo_rbac_router.post("/different-roles-different-parameters")
def parameter_restriction(
        validated_parameters: Annotated[
            DifferentRolesDifferentParameters,
            Depends()
        ]):
    return {"message": "OK"}
