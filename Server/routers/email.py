
from fastapi import APIRouter , status , HTTPException , Depends
from Server.database import getdb
from sqlalchemy.orm.session import Session
import secrets

import Server.config as config
import Server.utils as utils
import Server.schemas as schemas
import Server.models as models
from Server.routers.auth import getCurrentUser

emailRouter = APIRouter(tags=["Email"])


# ----------------------------VERIFY EMAIL-------------------------
@emailRouter.get("/verify/{secret}" , status_code=status.HTTP_202_ACCEPTED)
def verifyEmail(secret:str , db:Session = Depends(getdb)):

    secretRow = db.query(models.EmailVerify).filter(models.EmailVerify.secret == secret).first()
    
    if secretRow == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Invalid URL")

    student = db.query(models.Student).filter(models.Student.id == secretRow.studentId).first()
    student.verified = True

    db.delete(secretRow)
    db.commit()

    return {"message" : "Email Verified"}
# ------------------------------------------------------------------


# ----------------------------SEND VERIFICATION EMAIL-------------------------
@emailRouter.post("/verify")
async def sendVerificationMail(data:schemas.email , db:Session = Depends(getdb)):

    student = db.query(models.Student).filter(models.Student.email == data.email).first()

    if student == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Account with this email not found")

    if student.verified == True:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="Email already verified")
    
    secretRow = db.query(models.EmailVerify).filter(models.EmailVerify.studentId == student.id).first()

    subject = "Email Verification"
    html = f"""<a href='http://192.168.69.167:8000/verify/{secretRow.secret}'>Click here to verify your email</a>"""

    await utils.sendMail(recipients=[student.email] , subject=subject , html=html)

    return {"message" : "Verification mail Sent"}
# ------------------------------------------------------------------


