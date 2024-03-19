from pydantic import BaseModel
from typing import Dict, Union, Optional


class Function(BaseModel):
    function_name: str
    function_docs: str
    function_params: Optional[Dict[str, Union[str, int, bool, float, None]]] = None
    function_body: str
    function_code: str