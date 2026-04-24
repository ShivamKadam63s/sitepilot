from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, create_access_token, get_current_user
)
from app.models.models import User
from app.schemas.schemas import LoginRequest, TokenResponse, UserOut, TenantOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_access_token(
        subject=user.id,
        extra={"tenant_id": user.tenant_id, "role": user.role},
    )
    return TokenResponse(
        access_token=token,
        user=UserOut.model_validate(user),
        tenant=TenantOut.model_validate(user.tenant),
    )


@router.post("/logout", status_code=204)
def logout():
    # JWT is stateless — client simply discards the token.
    # For token blocklisting, add Redis entry here.
    return


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user":   UserOut.model_validate(current_user),
        "tenant": TenantOut.model_validate(current_user.tenant),
    }
