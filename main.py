from fastapi import FastAPI #importing fastapi class
app = FastAPI(
    title="Automotive backend API",
    description="Predictive maintenance system for vehicles",
    version="0.1.0"
)
# creating entire backend API application ^
#root endpoint-homepage
@app.get("/")
def read_root():#function runs when someone uses /
    return {
        "message":"Welcome to Automotive backend API",
        "status": "running",
        "version":"0.1.0"
    }
    #Send this data back as JSON
    #Dictionary becomes JSON automatically!
@app.get("/health")
def heath_check():
    return {"status":"healthy",
            "message":"API is working properly"
            }
