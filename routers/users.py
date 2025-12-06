"""User management router."""

import random
import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from neo4j.time import Date

from models import (
    UserCreate, UserUpdate, UserVerify,
    UserCreateResponse, UserListResponse, UserDetailResponse, VerifyResponse
)
from utils.database import get_driver
from utils.user_helpers import build_update_clauses, format_dob


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    summary="Create or fetch user by mobile",
    description=(
        "Create a new user if the given mobile does not exist, or return the existing "
        "user if it already exists. A stable Neo4j UUID is assigned on first creation."
    ),
    response_model=UserCreateResponse,
    responses={
        200: {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "message": "User already exists",
                        "user": {
                            "id": "uuid-123",
                            "mobile": "9876543210",
                            "first_name": "John",
                            "last_name": "Doe",
                            "refered_by_mobile": "9876543211",
                            "refered_by_name": "Jane Doe"
                        }
                    }
                }
            }
        },
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 201,
                        "status": "success",
                        "message": "User created or updated",
                        "user": {
                            "id": "uuid-456",
                            "mobile": "9876543210",
                            "first_name": "John",
                            "last_name": "Doe",
                            "refered_by_mobile": "9876543211",
                            "refered_by_name": "Jane Doe"
                        }
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
@router.post(
    "/",
    include_in_schema=False,
)
async def create_user(user_data: UserCreate):
    """Create or fetch user by mobile number."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                # Check if user already exists
                existing = session.run(
                    "MATCH (u:User {mobile: $mobile}) RETURN u",
                    mobile=user_data.mobile
                ).single()

                if existing:
                    existing_props = dict(existing["u"])
                    return {
                        "statuscode": 200,
                        "status": "success",
                        "message": "User already exists",
                        "user": existing_props
                    }

                # Create or update user, assigning a stable unique id on first creation
                result = session.run(
                    "MERGE (u:User {mobile: $mobile}) "
                    "ON CREATE SET u.id = randomUUID() "
                    "SET u.first_name = $first_name,u.last_name = $last_name,u.mobile = $mobile,u.refered_by_mobile = $refered_by_mobile,u.refered_by_name = $refered_by_name "
                    "RETURN u.id AS id, u.mobile AS mobile, u.first_name AS first_name, u.last_name AS last_name,u.refered_by_mobile AS refered_by_mobile,u.refered_by_name AS refered_by_name",
                    **user_data.dict()
                )
                record = result.single()
                return {
                    "statuscode": 201,
                    "status": "success",
                    "message": "User created or updated",
                    "user": {
                        "id": record["id"],
                        "mobile": record["mobile"],
                        "first_name": record["first_name"],
                        "last_name": record["last_name"],
                        "refered_by_mobile": record["refered_by_mobile"],
                        "refered_by_name": record["refered_by_name"],
                    },
                }
        finally:
            driver.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{mobile}",
    summary="Update user by mobile",
    description="Update profile and KYC details for a user identified by mobile number.",
    response_model=Dict[str, Any],
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "message": "User updated successfully",
                        "updated_fields": 3,
                        "user": {
                            "id": "uuid-123",
                            "mobile": "9876543210",
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john@example.com"
                        }
                    }
                }
            }
        },
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_user(mobile: str, user_update: UserUpdate):
    """Update user by mobile number."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                # Check if user exists
                result = session.run("MATCH (u:User {mobile: $mobile}) RETURN u", mobile=mobile)
                user = result.single()
                
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                set_clauses, params = build_update_clauses(user_update.dict(exclude_unset=True))
                params["mobile"] = mobile
                
                if set_clauses:
                    query = f"MATCH (u:User {{mobile: $mobile}}) SET {', '.join(set_clauses)} RETURN u"
                    result = session.run(query, **params)
                    updated = result.single()["u"] if result.single() else None
                    updated_data = dict(updated) if updated is not None else None
                else:
                    updated_data = None
               
                return {"statuscode": 200, "status": "success", "message": "User updated successfully", "updated_fields": len(set_clauses), "user": updated_data}
        finally:
            driver.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/id/{user_id}",
    summary="Update user by UUID",
    description="Update profile and KYC details for a user identified by Neo4j UUID id.",
    response_model=Dict[str, Any],
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "message": "User updated successfully",
                        "updated_fields": 2,
                        "user": {
                            "id": "uuid-123",
                            "mobile": "9876543210",
                            "dob": "15-01-1990"
                        }
                    }
                }
            }
        },
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_user_by_id(user_id: str, user_update: UserUpdate):
    """Update user by UUID."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {id: $id}) RETURN u", id=user_id)
                user = result.single()

                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                set_clauses, params = build_update_clauses(user_update.dict(exclude_unset=True))
                params["id"] = user_id

                if set_clauses:
                    query = f"MATCH (u:User {{id: $id}}) SET {', '.join(set_clauses)} RETURN u"
                    result = session.run(query, **params)
                    record = result.single()
                    updated = record["u"] if record else None
                    updated_data = dict(updated) if updated is not None else None
                    # Convert dob to dd-mm-yyyy string if present
                    if updated_data and 'dob' in updated_data:
                        updated_data['dob'] = format_dob(updated_data['dob'])
                else:
                    updated_data = None

                return {"statuscode": 200, "status": "success", "message": "User updated successfully", "updated_fields": len(set_clauses), "user": updated_data}
        finally:
            driver.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/referrals",
    summary="List unverified referred users",
    description="Return users who were referred but are not yet verified customers.",
    response_model=UserListResponse,
    responses={
        200: {
            "description": "List of unverified referred users",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "users": [
                            {
                                "id": "uuid-123",
                                "mobile": "9876543210",
                                "first_name": "John",
                                "last_name": "Doe",
                                "refered_by_name": "Jane Doe",
                                "refered_by_mobile": "9876543211"
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def get_new_referrals():
    """Get list of unverified referred users."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User) WHERE u.verified = false OR u.verified is null RETURN u.id, u.mobile, u.first_name, u.last_name,u.refered_by_name,u.refered_by_mobile")
                users = [
                    {
                        "id": record["u.id"],
                        "mobile": record["u.mobile"],
                        "first_name": record["u.first_name"],
                        "last_name": record["u.last_name"],
                        "refered_by_name": record["u.refered_by_name"],
                        "refered_by_mobile": record["u.refered_by_mobile"]
                    }
                    for record in result
                ]
            return {"statuscode": 200, "status": "success", "users": users}
        finally:
            driver.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/customers",
    summary="List verified customers",
    description="Return all users marked as verified customers in Neo4j.",
    response_model=UserListResponse,
    responses={
        200: {
            "description": "List of verified customers",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "users": [
                            {
                                "id": "uuid-123",
                                "mobile": "9876543210",
                                "first_name": "John",
                                "last_name": "Doe",
                                "isFormFilled": True,
                                "refered_by_name": "Jane Doe",
                                "refered_by_mobile": "9876543211",
                                "verified": True
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def get_existing_customers():
    """Get list of verified customers."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {verified:true}) RETURN u.id, u.mobile, u.first_name, u.last_name, u.isFormFilled, u.refered_by_name, u.refered_by_mobile, u.verified")
                users = [
                    {
                        "id": record["u.id"],
                        "mobile": record["u.mobile"],
                        "first_name": record["u.first_name"],
                        "last_name": record["u.last_name"],
                        "isFormFilled": record["u.isFormFilled"],
                        "refered_by_name": record["u.refered_by_name"],
                        "refered_by_mobile": record["u.refered_by_mobile"],
                        "verified": record["u.verified"]
                    }
                    for record in result
                ]
            return {"statuscode": 200, "status": "success", "users": users}
        finally:
            driver.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{mobile}",
    summary="Get user details by mobile",
    description="Fetch full user node properties using the mobile number.",
    response_model=UserDetailResponse,
    responses={
        200: {
            "description": "User details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "user": {
                            "id": "uuid-123",
                            "mobile": "9876543210",
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john@example.com",
                            "verified": True
                        }
                    }
                }
            }
        },
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_details(mobile: str):
    """Get user details by mobile number."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {mobile: $mobile}) RETURN u", mobile=mobile)
                user_record = result.single()
                
                if not user_record:
                    raise HTTPException(status_code=404, detail="User not found")
                
                user_node = user_record["u"]
                user_data = dict(user_node)
                
                return {"statuscode": 200, "status": "success", "user": user_data}
        finally:
            driver.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/id/{user_id}",
    summary="Get user details by UUID",
    description="Fetch full user node properties using the generated UUID id. Date of birth is formatted as DD-MM-YYYY.",
    response_model=UserDetailResponse,
    responses={
        200: {
            "description": "User details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "user": {
                            "id": "uuid-123",
                            "mobile": "9876543210",
                            "first_name": "John",
                            "last_name": "Doe",
                            "dob": "15-01-1990",
                            "verified": True
                        }
                    }
                }
            }
        },
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_details_by_id(user_id: str):
    """Fetch full user details using generated unique id instead of mobile."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {id: $id}) RETURN u", id=user_id)
                user_record = result.single()

                if not user_record:
                    raise HTTPException(status_code=404, detail="User not found")

                user_node = user_record["u"]
                user_data = dict(user_node)
                # Convert dob to dd-mm-yyyy string if present
                if 'dob' in user_data:
                    user_data['dob'] = format_dob(user_data['dob'])

                return {"statuscode": 200, "status": "success", "user": user_data}
        finally:
            driver.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/verify",
    summary="Verify referred user and issue OTP",
    description=(
        "Verify whether a referred user exists. If already verified, returns user "
        "details. If not verified, generates and returns an OTP with user details."
    ),
    response_model=VerifyResponse,
    responses={
        200: {
            "description": "User verification status",
            "content": {
                "application/json": {
                    "examples": {
                        "already_verified": {
                            "summary": "User already verified",
                            "value": {
                                "statuscode": 200,
                                "status": "success",
                                "message": "User already verified",
                                "user": {
                                    "id": "uuid-123",
                                    "mobile": "9876543210",
                                    "verified": True
                                }
                            }
                        },
                        "new_verification": {
                            "summary": "New user verified with OTP",
                            "value": {
                                "statuscode": 200,
                                "status": "success",
                                "message": "New user verified",
                                "otp": "123456",
                                "user": {
                                    "id": "uuid-123",
                                    "mobile": "9876543210",
                                    "verified": False
                                }
                            }
                        }
                    }
                }
            }
        },
        300: {"description": "User not found or not a new referral"},
        500: {"description": "Internal server error"}
    }
)
async def verify_user(user_data: UserVerify):
    """Verify user and issue OTP if needed."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                # Check if user exists and is new_referral and not verified
                result = session.run(
                    "MATCH (u:User {mobile: $mobile}) RETURN u.referral_type AS type, u.verified AS verified, properties(u) AS user_props",
                    mobile=user_data.mobile
                )
                record = result.single()
                if not record:
                    raise HTTPException(status_code=300, detail="User not found")
                if record["verified"]:
                    user_props = dict(record["user_props"])
                    # Convert dob to dd-mm-yyyy string if present
                    if 'dob' in user_props:
                        user_props['dob'] = format_dob(user_props['dob'])
                    return {"statuscode": 200, "status": "success", "message": "User already verified", "user": user_props}
                elif record:
                    # Generate OTP
                    otp = str(random.randint(100000, 999999))
                    user_props = dict(record["user_props"])
                    user_props['verified'] = False
                    user_props['otp'] = otp
                    # Convert dob to dd-mm-yyyy string if present
                    if 'dob' in user_props:
                        user_props['dob'] = format_dob(user_props['dob'])
                    return {"statuscode": 200, "status": "success", "message": "New user verified", "otp": otp, "user": user_props}
                else:
                    raise HTTPException(status_code=300, detail="User not a new referral")
        finally:
            driver.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
