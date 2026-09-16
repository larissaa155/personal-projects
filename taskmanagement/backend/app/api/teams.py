from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.team import Team, team_members
from app.models.task import Task
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all teams"""
    query = db.query(Team).options(
        joinedload(Team.created_by),
        joinedload(Team.members)
    )
    
    #If regular user, only show teams they're a member of
    if current_user.role.value == "member":
        query = query.join(team_members).filter(team_members.c.user_id == current_user.id)
    
    teams = query.offset(skip).limit(limit).all()
    return teams

@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team"""
    #Only admin and managers can create teams
    if current_user.role.value not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    new_team = Team(
        name=team_data.name,
        description=team_data.description,
        created_by_id=current_user.id
    )
    
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    #Add creator as member
    stmt = team_members.insert().values(team_id=new_team.id, user_id=current_user.id)
    db.execute(stmt)
    db.commit()
    
    #Refresh with relationships
    team = db.query(Team).options(
        joinedload(Team.created_by),
        joinedload(Team.members)
    ).filter(Team.id == new_team.id).first()
    
    return team

@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team by ID"""
    team = db.query(Team).options(
        joinedload(Team.created_by),
        joinedload(Team.members),
        joinedload(Team.tasks)
    ).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    #Check if user is member or admin
    is_member = any(member.id == current_user.id for member in team.members)
    if current_user.role.value == "member" and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )
    
    return team

@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    #Check permissions
    if current_user.role.value not in ["admin", "manager"] and team.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in team_data.dict(exclude_unset=True).items():
        setattr(team, field, value)
    
    db.commit()
    db.refresh(team)
    
    #Refresh with relationships
    team = db.query(Team).options(
        joinedload(Team.created_by),
        joinedload(Team.members)
    ).filter(Team.id == team_id).first()
    
    return team

@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    #Only admin can delete teams
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete teams"
        )
    
    db.delete(team)
    db.commit()

@router.post("/teams/{team_id}/members/{user_id}")
async def add_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add user to team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #Check permissions
    if current_user.role.value not in ["admin", "manager"] and team.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    #Check if already member
    if user in team.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team"
        )
    
    stmt = team_members.insert().values(team_id=team_id, user_id=user_id)
    db.execute(stmt)
    db.commit()
    
    return {"message": "User added to team successfully"}

@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove user from team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    #Check permissions
    if current_user.role.value not in ["admin", "manager"] and team.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    #Cannot remove last admin/creator
    if user_id == team.created_by_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove team creator"
        )
    
    stmt = team_members.delete().where(
        team_members.c.team_id == team_id,
        team_members.c.user_id == user_id
    )
    result = db.execute(stmt)
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not a member of this team")
    
    return {"message": "User removed from team successfully"}