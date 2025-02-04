from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.engine import check_availability, get_session
from app.models.AppStatus import AppStatus

router = APIRouter()

@router.get("/status", status_code=HTTPStatus.OK)
def status(session: Session = Depends(get_session)) -> AppStatus:
    return AppStatus(database=check_availability(session))


