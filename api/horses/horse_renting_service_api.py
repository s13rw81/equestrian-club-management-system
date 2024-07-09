from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from data.dbapis.horses.horse_renting_service_queries import get_renting_horse_by_id
from logic.auth import get_current_user
from models.horse.horse_internal import InternalSellHorse
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

from .models.horse_renting_service import HorseRentingItem
