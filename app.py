import os
import random
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from neo4j import GraphDatabase
import datetime
from neo4j.time import Date

# Load environment variables from .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# Validate Neo4j environment variables
if not os.getenv("NEO4J_URI"):
    raise RuntimeError("NEO4J_URI is missing. Ensure .env is correctly configured.")
if not os.getenv("NEO4J_PASSWORD"):
    raise RuntimeError("NEO4J_PASSWORD is missing. Ensure .env is correctly configured.")

app = Flask(__name__)

# CORS
CORS(app, origins=["*"], supports_credentials=True)

# Static files directory
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Neo4j connection
URI = os.getenv("NEO4J_URI")
AUTH = ("neo4j", os.getenv("NEO4J_PASSWORD"))

def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

# Simple validation functions
def validate_user_create(data):
    """Validate user creation data"""
    if not data:
        return False, "No data provided"
    
    required_fields = ['mobile', 'first_name', 'last_name', 'refered_by_mobile','refered_by_name']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    return True, None

def validate_user_verify(data):
    """Validate user verification data"""
    if not data:
        return False, "No data provided"
    
    required_fields = ['mobile', 'device_id', 'device_model']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    return True, None

def validate_purchase(data):
    """Validate purchase data"""
    if not data:
        return False, "No data provided"
    
    required_fields = ['User_mobile', 'item', 'details']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    return True, None

def build_update_clauses(user_update: dict) -> tuple[list, dict]:
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

@app.route("/", methods=["GET"])
def read_root():
    """Serve the main frontend page"""
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return send_from_directory("static", "index.html")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Markwave Admin Dashboard</title>
        <style>
            body { font-family: sans-serif; margin: 2rem; }
            h1 { color: #333; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>Markwave Admin Dashboard</h1>
        <p>Flask backend is running.</p>
        <p><a href="/health">Health Check</a></p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route("/static/<path:filename>")
def static_files(filename):
    """Serve static files"""
    return send_from_directory(STATIC_DIR, filename)

@app.route("/favicon.ico")
def favicon():
    """Return a minimal favicon to avoid 404s"""
    favicon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return send_from_directory(STATIC_DIR, "favicon.ico")
    return jsonify({"status": "no favicon"})

@app.route("/health")
def health_check():
    return jsonify({"status": "ok"})

@app.route("/users/", methods=["POST"])
def create_user():
    is_valid, error_message = validate_user_create(request.json)
    if not is_valid:
        return jsonify({"statuscode": 400, "status": "error", "message": error_message}), 400
    
    user_data = request.json
    
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                # Check if user already exists
                existing = session.run(
                    "MATCH (u:User {mobile: $mobile}) RETURN u",
                    mobile=user_data['mobile']
                ).single()

                if existing:
                    existing_props = dict(existing["u"])
                    return jsonify({
                        "statuscode": 200,
                        "status": "success",
                        "message": "User already exists",
                        "user": existing_props
                    })

                # Create or update user, assigning a stable unique id on first creation
                result = session.run(
                    "MERGE (u:User {mobile: $mobile}) "
                    "ON CREATE SET u.id = randomUUID() "
                    "SET u.first_name = $first_name,u.last_name = $last_name,u.mobile = $mobile,u.refered_by_mobile = $refered_by_mobile,u.refered_by_name = $refered_by_name "
                    "RETURN u.id AS id, u.mobile AS mobile, u.first_name AS first_name, u.last_name AS last_name,u.refered_by_mobile AS refered_by_mobile,u.refered_by_name AS refered_by_name",
                    **user_data
                )
                record = result.single()
                return jsonify({
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
                })
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/<mobile>", methods=["PUT"])
def update_user(mobile):
    if not request.json:
        return jsonify({"statuscode": 400, "status": "error", "message": "No data provided"}), 400
    
    user_update = request.json
    
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                # Check if user exists
                result = session.run("MATCH (u:User {mobile: $mobile}) RETURN u", mobile=mobile)
                user = result.single()
                
                if not user:
                    return jsonify({"statuscode": 404, "status": "error", "message": "User not found"}), 404
                
                set_clauses, params = build_update_clauses(user_update)
                params["mobile"] = mobile
                
                if set_clauses:
                    query = f"MATCH (u:User {{mobile: $mobile}}) SET {', '.join(set_clauses)} RETURN u"
                    result = session.run(query, **params)
                    updated = result.single()["u"] if result.single() else None
                    updated_data = dict(updated) if updated is not None else None
                else:
                    updated_data = None
               
                return jsonify({"statuscode": 200, "status": "success", "message": "User updated successfully", "updated_fields": len(set_clauses), "user": updated_data})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/id/<user_id>", methods=["PUT"])
def update_user_by_id(user_id):
    if not request.json:
        return jsonify({"statuscode": 400, "status": "error", "message": "No data provided"}), 400
    
    user_update = request.json
    
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {id: $id}) RETURN u", id=user_id)
                user = result.single()

                if not user:
                    return jsonify({"statuscode": 404, "status": "error", "message": "User not found"}), 404

                set_clauses, params = build_update_clauses(user_update)
                params["id"] = user_id

                if set_clauses:
                    query = f"MATCH (u:User {{id: $id}}) SET {', '.join(set_clauses)} RETURN u"
                    result = session.run(query, **params)
                    record = result.single()
                    updated = record["u"] if record else None
                    updated_data = dict(updated) if updated is not None else None
                    # Convert dob to dd-mm-yyyy string if present
                    if updated_data and 'dob' in updated_data:
                       dob = updated_data['dob']
                       if isinstance(dob, datetime.date):
                            updated_data['dob'] = dob.strftime('%d-%m-%Y')
                       elif isinstance(dob, Date):
                            updated_data['dob'] = f"{dob.day:02d}-{dob.month:02d}-{dob.year}"
                else:
                    updated_data = None

                return jsonify({"statuscode": 200, "status": "success", "message": "User updated successfully", "updated_fields": len(set_clauses), "user": updated_data})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/referrals", methods=["GET"])
def get_new_referrals():
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
            return jsonify({"statuscode": 200, "status": "success", "users": users})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/customers", methods=["GET"])
def get_existing_customers():
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
            return jsonify({"statuscode": 200, "status": "success", "users": users})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/<mobile>", methods=["GET"])
def get_user_details(mobile):
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {mobile: $mobile}) RETURN u", mobile=mobile)
                user_record = result.single()
                
                if not user_record:
                    return jsonify({"statuscode": 404, "status": "error", "message": "User not found"}), 404
                
                user_node = user_record["u"]
                user_data = dict(user_node)
                
                return jsonify({"statuscode": 200, "status": "success", "user": user_data})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/id/<user_id>", methods=["GET"])
def get_user_details_by_id(user_id):
    """Fetch full user details using generated unique id instead of mobile."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (u:User {id: $id}) RETURN u", id=user_id)
                user_record = result.single()

                if not user_record:
                    return jsonify({"statuscode": 404, "status": "error", "message": "User not found"}), 404

                user_node = user_record["u"]
                user_data = dict(user_node)
                # Convert dob to dd-mm-yyyy string if present
                if 'dob' in user_data:
                    dob = user_data['dob']
                    if isinstance(dob, datetime.date):
                        user_data['dob'] = dob.strftime('%d-%m-%Y')
                    elif isinstance(dob, Date):
                        user_data['dob'] = f"{dob.day:02d}-{dob.month:02d}-{dob.year}"

                return jsonify({"statuscode": 200, "status": "success", "user": user_data})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/products/<product_id>", methods=["GET"])
def get_product_details(product_id):
    """Return product details for a given product id from Neo4j database."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (n:BUFFALO) WHERE n.id=$product_id RETURN n", product_id=product_id)
                record = result.single()
                
                if not record:
                    return jsonify({"statuscode": 404, "status": "error", "message": "Product not found"}), 404
                
                product_node = record["n"]
                product_data = dict(product_node)
                
                return jsonify({"statuscode": 200, "status": "success", "product": product_data})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/products", methods=["GET"])
def get_products():
    """Return all buffalo products stored in Neo4j as PRODUCT:BUFFALO nodes."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (p:PRODUCT:BUFFALO) RETURN p")
                products = [dict(record["p"]) for record in result]
            return jsonify({"statuscode": 200, "status": "success", "products": products})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/users/verify", methods=["POST"])
def verify_user():
    is_valid, error_message = validate_user_verify(request.json)
    if not is_valid:
        return jsonify({"statuscode": 400, "status": "error", "message": error_message}), 400
    
    user_data = request.json
    
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                # Check if user exists and is new_referral and not verified
                result = session.run(
                    "MATCH (u:User {mobile: $mobile}) RETURN u.referral_type AS type, u.verified AS verified, properties(u) AS user_props",
                    mobile=user_data['mobile']
                )
                record = result.single()
                if not record:
                    return jsonify({"statuscode": 300, "status": "error", "message": "User not found"}), 300
                if record["verified"]:
                    user_props = dict(record["user_props"])
                    # Convert dob to dd-mm-yyyy string if present
                    if 'dob' in user_props:
                        dob = user_props['dob']
                        if isinstance(dob, datetime.date):
                            user_props['dob'] = dob.strftime('%d-%m-%Y')
                        elif isinstance(dob, Date):
                            user_props['dob'] = f"{dob.day:02d}-{dob.month:02d}-{dob.year}"
                    return jsonify({"statuscode": 200, "status": "success", "message": "User already verified", "user": user_props})
                elif record:
                    # Generate OTP
                    otp = str(random.randint(100000, 999999))
                    user_props = dict(record["user_props"])
                    user_props['verified'] = False
                    user_props['otp'] = otp
                    # Convert dob to dd-mm-yyyy string if present
                    if 'dob' in user_props:
                        dob = user_props['dob']
                        if isinstance(dob, datetime.date):
                            user_props['dob'] = dob.strftime('%d-%m-%Y')
                        elif isinstance(dob, Date):
                            user_props['dob'] = f"{dob.day:02d}-{dob.month:02d}-{dob.year}"
                    return jsonify({"statuscode": 200, "status": "success", "message": "New user verified", "otp": otp, "user": user_props})
                else:
                    return jsonify({"statuscode": 300, "status": "error", "message": "User not a new referral"}), 300
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

@app.route("/purchases/", methods=["POST"])
def create_purchase():
    is_valid, error_message = validate_purchase(request.json)
    if not is_valid:
        return jsonify({"statuscode": 400, "status": "error", "message": error_message}), 400
    
    purchase_data = request.json
    
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                session.run(
                    "MATCH (u:User {mobile: $User_mobile}) "
                    "CREATE (u)-[:PURCHASED {item: $item, details: $details}]->(p:Purchase {id: randomUUID()})",
                    **purchase_data
                )
            return jsonify({"statuscode": 200, "status": "success", "message": "Purchase recorded"})
        finally:
            driver.close()
    except Exception as e:
        return jsonify({"statuscode": 500, "status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
