from dotenv import load_dotenv

load_dotenv('config/environ/.env')


def response(data=None, success=False, message="Failed", error=None, offset=None, limit=None, total=0):
    return {
        "success": success,
        "message": message,
        "data": data,
        "error": error
#         "total": total,
#         "limit": limit,
#         "offset": offset,
    }

