from fastapi import FastAPI, Depends, status, HTTPException
from .database import engine, SessionLocal  # Import the database engine and SessionLocal function
from sqlalchemy.orm import Session
from . import schemas, models  # Import your schemas and models

app = FastAPI()

# Create database tables based on the defined models
models.Base.metadata.create_all(engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new blog entry
@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create_blog(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

# Delete a blog entry by ID
@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(id: int, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()
    return "Blog has been deleted successfully"

# Update a blog entry by ID
@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_blog(id: int, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")

    for attr, value in request.dict().items():
        setattr(blog, attr, value)

    db.commit()
    return 'Blog has been updated successfully'

# Get all blog entries
@app.get('/blog', status_code=status.HTTP_200_OK)
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

# Get a single blog entry by ID
@app.get('/blog/{id}', status_code=status.HTTP_200_OK)
def get_single_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} does not exist")
    
    return blog
