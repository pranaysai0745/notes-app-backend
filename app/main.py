from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db

from app.models import User, Note

from app.schemas import (
    UserCreate,
    NoteCreate
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()


# HOME API
@app.get("/")
def home():

    return {
        "message": "Notes API Running Successfully"
    }


# REGISTER API
@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(
        user.password
    )

    # Create new user
    new_user = User(
        email=user.email,
        password=hashed_password
    )

    # Save to database
    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


# LOGIN API
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Find user by email
    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # Check user exists
    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    valid_password = verify_password(
        form_data.password,
        existing_user.password
    )

    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = create_access_token(
        data={"sub": existing_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# CREATE NOTE API
@app.post("/notes")
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Create note
    new_note = Note(
        title=note.title,
        content=note.content,
        owner_id=current_user.id
    )

    # Save note
    db.add(new_note)

    db.commit()

    db.refresh(new_note)

    return {
        "message": "Note created successfully"
    }


# GET ALL NOTES API
@app.get("/notes")
def get_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Get all notes of logged-in user
    notes = db.query(Note).filter(
        Note.owner_id == current_user.id
    ).all()

    return notes


# GET SINGLE NOTE API
@app.get("/notes/{id}")
def get_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == id,
        Note.owner_id == current_user.id
    ).first()

    if not note:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


# UPDATE NOTE API
@app.put("/notes/{id}")
def update_note(
    id: int,
    updated_note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == id,
        Note.owner_id == current_user.id
    ).first()

    if not note:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    note.title = updated_note.title
    note.content = updated_note.content

    db.commit()

    return {
        "message": "Note updated successfully"
    }


# DELETE NOTE API
@app.delete("/notes/{id}")
def delete_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == id,
        Note.owner_id == current_user.id
    ).first()

    if not note:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    db.delete(note)

    db.commit()

    return {
        "message": "Note deleted successfully"
    }


# SHARE NOTE API
@app.post("/notes/{id}/share")
def share_note(
    id: int,
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == id,
        Note.owner_id == current_user.id
    ).first()

    if not note:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    shared_user = db.query(User).filter(
        User.email == email
    ).first()

    if not shared_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": f"Note shared with {email}"
    }


# SEARCH NOTES API
@app.get("/search")
def search_notes(
    keyword: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notes = db.query(Note).filter(
        Note.owner_id == current_user.id,
        Note.title.contains(keyword)
    ).all()

    return notes


# ABOUT API
@app.get("/about")
def about():

    return {
        "name": "Pranay",
        "email": "pranaysaibly@gmail.com",
        "my_features": {
            "search_notes": "Allows users to search notes using keywords"
        }
    }