from fastapi import  APIRouter, Response, Depends
from models.user import UserIn, UserOut, UserInDB, UserLogin
from config.database import users_collection
from bson import ObjectId
import os
import replicate
from config.database import functions_collection
import subprocess
from starlette.responses import FileResponse
from utils.hashing import get_password_hash, verify_password
from utils.access_token import create_access_token, decode_token
from utils.check_user_auth import check_user_auth
from models.prompt import Prompt


os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")

user_router = APIRouter()


@user_router.get("/me", dependencies=[Depends(check_user_auth)], response_model=UserOut)
def get_user(x_user_auth:str = Depends(check_user_auth)):
    decoded_data = decode_token(x_user_auth)
    user = users_collection.find_one({"_id": ObjectId(decoded_data["_id"])})
    return user




@user_router.post("/signup")
async def signup(user: UserIn, response: Response):
    # Check if user already exists

    

    user_dict = dict(user)
    # Hash the password
    hashed_password = get_password_hash(user_dict["password"])
    

    user_in_db = UserInDB(**user_dict, hashed_password=hashed_password)
    
    # Create user in the database
    result = users_collection.insert_one(dict(user_in_db))

    if result.acknowledged:
        response.headers["X-User-Auth"] = create_access_token(str(result.inserted_id)) 
        # return users_collection.find_one({"_id": result.inserted_id})
        return {"message": "Registered Successfully!"}

    





@user_router.post("/login")
async def login(user_login: UserLogin, response: Response):
    user = users_collection.find_one({"email": user_login.email})
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        return {
            "message" : "Uaser can not be logged in!"
        }
    
    response.headers["X-User-Auth"] = create_access_token(str(user["_id"]))    
    return {"message": "Login successful"}







@user_router.post("/prompt", dependencies=[Depends(check_user_auth)])
async def handlePrompt(prompt: Prompt, x_user_auth:str = Depends(check_user_auth) ):
    
    code_file_filepath = "C:\\Users\\hp\\Documents\\FYP\\Blender_Model_Generator\\FYP-Backend\\generated_codes\\code.py"
    if os.path.exists(code_file_filepath):
        os.remove(code_file_filepath)


    prompt_text = prompt.text
    # Update user prompts and generation count
    user_id = decode_token(x_user_auth)
    user = users_collection.find_one({"_id": user_id["_id"]})

    if user:
        # Update prompts array and increment generation_count
        users_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {
                "$push": {"prompts": prompt_text},
                "$inc": {"generation_count": 1}
            }
        )


    all_functions = functions_collection.find({})
    import_statements = [
        "import bpy\n",
        "import random\n",
        "import numpy as np\n",
        "import random\n"
    ]
    default_functions = [
        "\ndef delete_all_objects():\n\tfor object in bpy.data.objects:\n\t\tbpy.data.objects.remove(object)\n",
        "\ndef decrease_size(obj):\n\tobj.delta_scale = [ obj.delta_scale[0] - 1.4 / 1.5, obj.delta_scale[1] - 1.4 / 1.5, obj.delta_scale[2] - 1.4 / 1.5 ]\n",
        "\ndef add_shrinkwrap(data, target):\n\tcon = data.constraints.new('SHRINKWRAP')\n\tcon.target = target\n\tcon.shrinkwrap_type = 'PROJECT'\n\tcon.project_axis = 'NEG_Z'\n"
    ]

    function_docs = []
    func_name_and_code = []

    for function in all_functions:
        function_docs.append({
            "function_name" : function["function_name"],
            "function_docs": function["function_docs"],
            "function_params": function["function_params"]
        })

        func_name_and_code.append({
            "function_name" : function["function_name"],
            "function_code" : function["function_code"]
        })


    response_1 = replicate.run(
    "meta/llama-2-70b-chat:2d19859030ff705a87c746f7e96eea03aefb71f166725aee39692f1476566d48",
    input={
        "debug": True,
        "top_p": 1,
        "prompt": prompt_text,
        "temperature": 0.5,
        "system_prompt": f"You are a helpful and intelligent assistant. Always answer as helpfully as possible, while being safe. Analyze these docs of different functions and based on the input prompt, choose the best functions that we can use. Only provide the names of the functions that we have to use. This is the list explaining all the functions: {function_docs}. Only provide the names of the function in response. Don't give any other details.\n\n",
        "max_new_tokens": 1500,
        "min_new_tokens": -1
    }
    )
    output_1 = []
    for item in response_1:
        output_1.append(item)
    output_1 = "".join(output_1)

    function_codes = []

    for function in all_functions:
        function_codes.append(function["function_code"])


        
    function_names = []
    # all_func_names = []
    for function in function_docs:
        # all_func_names.append(function["function_name"])
        if function["function_name"] in output_1:
            function_names.append(function["function_name"])

    final_code = []
    all_codes = []
    for func in func_name_and_code:
        all_codes.append(func["function_code"])
        if func["function_name"] in function_names:
            final_code.append(func["function_code"])


    # Create a directory for the generated codes
    if not os.path.exists('generated_codes'):
        os.makedirs('generated_codes')

    

    # write import statements
    for imp in import_statements:
        with open(f'generated_codes/code.py', 'a') as f:
            f.write(imp)

    # write default functions.
    for def_func in default_functions:
        with open(f'generated_codes/code.py', 'a') as f:
            f.write(def_func) 


    for func in final_code:
        with open(f'generated_codes/code.py', 'a') as f:
            f.write(func+"\n")

    # save as
    with open(f'generated_codes/code.py', 'a') as f:
            f.write("\nbpy.ops.wm.save_as_mainfile(filepath='./generated_scene.blend')\n")
    

    command = ["C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe", "--background", "--python", "C:\\Users\\hp\\Documents\\FYP\\Blender_Model_Generator\\FYP-Backend\\generated_codes\\code.py"]

    subprocess.run(command)

    blend_file_path = code_file_filepath

 
    return FileResponse(blend_file_path, media_type="application/octet-stream")
        