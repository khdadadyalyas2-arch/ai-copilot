import ast
import os
from datetime import datetime

ALLOWED_WORKSPACE = os.path.abspath(os.getenv("WORKSPACE_DIR", "./workspace"))
os.makedirs(ALLOWED_WORKSPACE, exist_ok=True)

def safe_calculator(expression: str) -> str:
    """محاسبات ریاضی ایمن بدون خطر امنیتی"""
    allowed_nodes = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.USub, ast.UAdd
    )
    try:
        tree = ast.parse(expression, mode='eval')
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                return "خطا: فقط عملیات پایه ریاضی مجاز است."
        result = eval(compile(tree, filename='', mode='eval'), {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"خطا در محاسبه: {e}"

def get_current_time() -> str:
    """دریافت زمان و تاریخ فعلی"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def list_files() -> str:
    """مشاهده لیست فایل‌ها در پوشه مجاز"""
    try:
        files = os.listdir(ALLOWED_WORKSPACE)
        return "\n".join(files) if files else "پوشه خالی است."
    except Exception as e:
        return f"خطا: {e}"

def read_text_file(filename: str) -> str:
    """خواندن متن از فایل مجاز"""
    safe_path = os.path.abspath(os.path.join(ALLOWED_WORKSPACE, filename))
    if not safe_path.startswith(ALLOWED_WORKSPACE) or not os.path.exists(safe_path):
        return "خطا: دسترسی غیرمجاز یا فایل وجود ندارد."
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"خطا در خواندن فایل: {e}"

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "safe_calculator",
            "description": "انجام محاسبات ریاضی",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "عبارت ریاضی مثل 2+2"}},
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "دریافت تاریخ و ساعت سیستم",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "دیدن لیست فایل‌ها در پوشه کار",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

TOOL_MAP = {
    "safe_calculator": lambda args: safe_calculator(args.get("expression", "")),
    "get_current_time": lambda args: get_current_time(),
    "list_files": lambda args: list_files(),
}
