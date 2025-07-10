from fastapi import APIRouter, Depends
from .models import User
from .capitalcom_api import CapitalComAPI
from .auth import get_current_user

router = APIRouter()

@router.get("/assets")
def get_assets(user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        identifier=user.username,
        password=user.password,
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        demo=user.use_demo
    )
    api.session_token = user.cc_session_token
    instruments = api.get_all_instruments()  # Implement this in your CapitalComAPI
    return [
        {
            "symbol": inst["symbol"],
            "name": inst.get("name", ""),
            "type": inst.get("type", "")
        }
        for inst in instruments
    ]