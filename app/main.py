# app/main.py

from app.routes import user_routes  # We'll create this soon

app = ()

# Register routes
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to IOWEYOU"}
