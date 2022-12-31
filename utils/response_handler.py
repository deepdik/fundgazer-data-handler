from fastapi.responses import JSONResponse


def response(data=None, success=False, message="Failed", error=None, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "message": message,
            "data": data,
            "error": error
        })
