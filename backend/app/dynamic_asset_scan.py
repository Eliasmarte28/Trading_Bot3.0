from fastapi import APIRouter, Depends
from .models import User
from .capitalcom_api import CapitalComAPI
from .auth import get_current_user

router = APIRouter()

@router.get("/dynamic-assets")
def get_dynamic_assets(user: User = Depends(get_current_user), top_n: int = 5, window_minutes: int = 15):
    api = CapitalComAPI(
        identifier=user.username,
        password=user.password,
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        demo=user.use_demo
    )
    api.session_token = user.cc_session_token
    assets = api.get_top_volatile_assets(top_n=top_n, window_minutes=window_minutes)
    return assets