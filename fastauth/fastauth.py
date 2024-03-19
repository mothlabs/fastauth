from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register():
    pass


@router.post("/login")
async def login():
    pass
