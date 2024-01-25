from flask import Flask
from flask import request, Flask, jsonify
from flask_basicauth import BasicAuth
from pymongo.mongo_client import MongoClient

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'username'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
basic_auth = BasicAuth(app)

uri = "mongodb+srv://chollada:i2kYflYG6WfAHetF@cluster0.kua1tuq.mongodb.net/retryWrites=true&w=majority"

client = MongoClient(uri)
db = client["student"]
collection = db["std_info"]

@app.route("/", methods=["GET"])
def greet():
    return "<p>Welcome to Student Management API</p>"

@app.route("/students", methods=["GET"])
@basic_auth.required
def get_all_students():
    students = list(collection.find({}))
    student_list = []

    for student in students:
        student_data = {
            "id": str(student["_id"]),
            "Fullname": student["Fullname"],
            "Major": student["Major"],
            "GPA": student["GPA"]
        }
        student_list.append(student_data)

    return jsonify({"students": student_list})

@app.route("/students/<string:std_id>", methods=["GET"])
@basic_auth.required
def get_student(std_id):
    student = collection.find_one({"_id": std_id})

    if student:
        student_data = {
            "id": str(student["_id"]),
            "Fullname": student.get("Fullname", ""),
            "Major": student.get("Major", ""),
            "GPA": student.get("GPA", ""),
        }
        return jsonify({"student": student_data})
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route("/students", methods=["POST"])
@basic_auth.required
def create_student():
    data = request.get_json()

    existing_student = collection.find_one({"_id": data.get("_id")})
    if existing_student:
        return jsonify({"error": "Cannot create new student"}), 500

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client["student"]
    collection = db["std_info"]
    while True:
        print("===MENU===")
        print("1: show all records")
        print("2: insert record")
        print("3: update record")
        print("4: delete record")
        print("5: exit")
        choice = input("Please choose:")
        choice = int(choice)
        if choice==1:
            print(f'found {collection.count_documents({})} records')
            all_students = collection.find()
            for std in all_students:
                print(std)
        elif choice==2:
            id=input("Input Student id : ")
            name=input("Input Fullname : ")
            major=input("Input Major : ")
            gpa=input("Input GPA : ")
            gpa=float(gpa)
            try:
                collection.insert_one({"_id":id,
                                    "Fullname":name,
                                    "Major":major,
                                    "GPA":gpa
                                    })
            except Exception as e:
                print(e)
        elif choice == 3:
            id = input("Enter the Student ID to update: ")
            new_id = input("Input new Student ID: ")
            new_name = input("Input new Fullname: ")
            new_major = input("Input new Major: ")
            new_gpa = float(input("Input new GPA: "))
            try:
                result = collection.update_one(
                {"_id": id},
                {"$set": {
                "_id": new_id,
                "Fullname": new_name,
                "Major": new_major,
                "GPA": new_gpa
                }}
                 )
                if result.modified_count > 0:
                    print(f"Record with ID {id} updated successfully.")
                else:
                    print(f"No record found with ID {id}.")

            except Exception as e:
                print(f"Error updating record: {e}")
        elif choice == 4:
            id = input("Student ID : ")

            try:
                result = collection.delete_one({"_id": id})

                if result.deleted_count > 0:
                    print(f"Record with ID {id} deleted successfully.")

                else:
                    print(f"No record found with ID {id}.")

            except Exception as e:
                print(f"Error deleting record: {e}")
        elif choice==5:
            break
    new_student = {
        "_id": data.get("_id"),
        "Fullname": data.get("Fullname"),
        "Major": data.get("Major"),
        "GPA": data.get("GPA")
    }

    result = collection.insert_one(new_student)

    return jsonify({"student": new_student}), 200

@app.route("/students/<string:std_id>", methods=["PUT"])
@basic_auth.required
def update_student(std_id):
    data = request.get_json()

    existing_student = collection.find_one({"_id": std_id})

    if existing_student:
        updated_student = {
            "Fullname": data.get("Fullname", existing_student["Fullname"]),
            "Major": data.get("Major", existing_student["Major"]),
            "GPA": data.get("GPA", existing_student["GPA"])
        }

        collection.update_one({"_id": std_id}, {"$set": updated_student})

        return jsonify({"student": updated_student}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

except Exception as e:
    print(e)
finally:
    client.close()
@app.route("/students/<string:std_id>", methods=["DELETE"])
@basic_auth.required
def delete_student(std_id):
    existing_student = collection.find_one({"_id": std_id})

    if existing_student:
        collection.delete_one({"_id": std_id})
        return jsonify({"message": "Student deleted successfully"}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)