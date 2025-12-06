"""Pydantic models for request/response validation."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Request models
class UserCreate(BaseModel):
    mobile: str = Field(..., description="User's mobile number", example="9876543210")
    first_name: str = Field(..., description="User's first name", example="John")
    last_name: str = Field(..., description="User's last name", example="Doe")
    refered_by_mobile: str = Field(..., description="Referrer's mobile number", example="9876543211")
    refered_by_name: str = Field(..., description="Referrer's name", example="Jane Doe")

    class Config:
        json_schema_extra = {
            "example": {
                "mobile": "9876543210",
                "first_name": "John",
                "last_name": "Doe",
                "refered_by_mobile": "9876543211",
                "refered_by_name": "Jane Doe"
            }
        }


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Full name", example="John Doe")
    email: Optional[str] = Field(None, description="Email address", example="john@example.com")
    first_name: Optional[str] = Field(None, description="First name", example="John")
    last_name: Optional[str] = Field(None, description="Last name", example="Doe")
    gender: Optional[str] = Field(None, description="Gender", example="Male")
    occupation: Optional[str] = Field(None, description="Occupation", example="Engineer")
    dob: Optional[str] = Field(None, description="Date of birth (MM-DD-YYYY)", example="01-15-1990")
    address: Optional[str] = Field(None, description="Address", example="123 Main St")
    city: Optional[str] = Field(None, description="City", example="Mumbai")
    state: Optional[str] = Field(None, description="State", example="Maharashtra")
    aadhar_number: Optional[str] = Field(None, description="Aadhar number", example="1234-5678-9012")
    pincode: Optional[str] = Field(None, description="PIN code", example="400001")
    aadhar_front_image_url: Optional[str] = Field(None, description="Aadhar front image URL")
    aadhar_back_image_url: Optional[str] = Field(None, description="Aadhar back image URL")
    verified: Optional[bool] = Field(None, description="Verification status")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")


class UserVerify(BaseModel):
    mobile: str = Field(..., description="User's mobile number", example="9876543210")
    device_id: str = Field(..., description="Device ID", example="device123")
    device_model: str = Field(..., description="Device model", example="iPhone 12")


class Purchase(BaseModel):
    User_mobile: str = Field(..., description="User's mobile number", example="9876543210")
    item: str = Field(..., description="Item purchased", example="Buffalo Milk")
    details: str = Field(..., description="Purchase details", example="1 liter organic buffalo milk")


# Response models
class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")


class UserResponse(BaseModel):
    id: str = Field(..., description="User UUID")
    mobile: str = Field(..., description="Mobile number")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    refered_by_mobile: str = Field(..., description="Referrer mobile")
    refered_by_name: str = Field(..., description="Referrer name")


class StandardResponse(BaseModel):
    statuscode: int = Field(..., description="Status code")
    status: str = Field(..., description="Status message")
    message: str = Field(..., description="Response message")


class UserCreateResponse(StandardResponse):
    user: UserResponse = Field(..., description="User data")


class UserListResponse(StandardResponse):
    users: List[Dict[str, Any]] = Field(..., description="List of users")


class UserDetailResponse(StandardResponse):
    user: Dict[str, Any] = Field(..., description="User details")


class ProductResponse(BaseModel):
    statuscode: int = Field(..., description="Status code")
    status: str = Field(..., description="Status message")
    product: Dict[str, Any] = Field(..., description="Product data")


class ProductListResponse(BaseModel):
    statuscode: int = Field(..., description="Status code")
    status: str = Field(..., description="Status message")
    products: List[Dict[str, Any]] = Field(..., description="List of products")


class VerifyResponse(BaseModel):
    statuscode: int = Field(..., description="Status code")
    status: str = Field(..., description="Status message")
    message: str = Field(..., description="Response message")
    user: Dict[str, Any] = Field(..., description="User data")
    otp: Optional[str] = Field(None, description="Generated OTP if applicable")


class PurchaseResponse(StandardResponse):
    pass
