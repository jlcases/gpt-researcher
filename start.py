import os
import uvicorn

if __name__ == "__main__":
    os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
    uvicorn.run("api.main:app", reload=True)
