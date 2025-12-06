"""Helper functions for user management."""

import datetime
from typing import Dict, Any, Tuple, List


def build_update_clauses(user_update: dict) -> Tuple[List[str], Dict[str, Any]]:
    """Build Cypher SET clauses and parameters for user update."""
    set_clauses = []
    params = {}

    # Standard fields
    if user_update.get('name') is not None:
        set_clauses.append("u.name = $name")
        params["name"] = user_update['name']
    if user_update.get('email') is not None:
        set_clauses.append("u.email = $email")
        params["email"] = user_update['email']
        set_clauses.append("u.verified = true")
        set_clauses.append("u.isFormFilled = true")
    if user_update.get('first_name') is not None:
        set_clauses.append("u.first_name = $first_name")
        params["first_name"] = user_update['first_name']
    if user_update.get('last_name') is not None:
        set_clauses.append("u.last_name = $last_name")
        params["last_name"] = user_update['last_name']
    if user_update.get('gender') is not None:
        set_clauses.append("u.gender = $gender")
        params["gender"] = user_update['gender']
    if user_update.get('occupation') is not None:
        set_clauses.append("u.occupation = $occupation")
        params["occupation"] = user_update['occupation']
    if user_update.get('dob') is not None:
        try:
            dob_date = datetime.datetime.strptime(user_update['dob'], '%m-%d-%Y').date()
            set_clauses.append("u.dob = $dob")
            params["dob"] = dob_date
        except ValueError:
            # Invalid date format, skip or handle
            pass
    if user_update.get('address') is not None:
        set_clauses.append("u.address = $address")
        params["address"] = user_update['address']
    if user_update.get('city') is not None:
        set_clauses.append("u.city = $city")
        params["city"] = user_update['city']
    if user_update.get('state') is not None:
        set_clauses.append("u.state = $state")
        params["state"] = user_update['state']
    if user_update.get('aadhar_number') is not None:
        set_clauses.append("u.aadhar_number = $aadhar_number")
        params["aadhar_number"] = user_update['aadhar_number']
    if user_update.get('pincode') is not None:
        set_clauses.append("u.pincode = $pincode")
        params["pincode"] = user_update['pincode']
    if user_update.get('aadhar_front_image_url') is not None:
        set_clauses.append("u.aadhar_front_image_url = $aadhar_front_image_url")
        params["aadhar_front_image_url"] = user_update['aadhar_front_image_url']
    if user_update.get('aadhar_back_image_url') is not None:
        set_clauses.append("u.aadhar_back_image_url = $aadhar_back_image_url")
        params["aadhar_back_image_url"] = user_update['aadhar_back_image_url']
    if user_update.get('verified') is not None:
        set_clauses.append("u.verified = $verified")
        params["verified"] = user_update['verified']
    
    # Custom fields
    if user_update.get('custom_fields'):
        for key, value in user_update['custom_fields'].items():
            safe_key = key.replace(" ", "_").replace("-", "_")
            set_clauses.append(f"u.{safe_key} = ${safe_key}")
            params[safe_key] = value

    return set_clauses, params


def format_dob(dob) -> str:
    """Format date of birth to DD-MM-YYYY string."""
    from neo4j.time import Date
    
    if isinstance(dob, datetime.date):
        return dob.strftime('%d-%m-%Y')
    elif isinstance(dob, Date):
        return f"{dob.day:02d}-{dob.month:02d}-{dob.year}"
    return str(dob)
