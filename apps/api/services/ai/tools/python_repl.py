import sys
import io
import traceback
import math
from typing import Any
from .base import BaseTool

class PythonREPLTool(BaseTool):
    name = "python_repl"
    description = (
        "A tool that executes Python code for precise calculations, data processing, or algorithmic validation. "
        "Use print() statements to view the output. Inputs: code (string)."
    )

    def run(self, code: str = "", **kwargs) -> str:
        if not code:
            code = kwargs.get("input", kwargs.get("query", ""))
        if not code:
            return "Error: No code provided to execute."

        # Clean markdown code blocks if present
        cleaned_code = code.strip()
        if cleaned_code.startswith("```python"):
            cleaned_code = cleaned_code[9:]
        elif cleaned_code.startswith("```"):
            cleaned_code = cleaned_code[3:]
        if cleaned_code.endswith("```"):
            cleaned_code = cleaned_code[:-3]
        cleaned_code = cleaned_code.strip()

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        redirected_error = io.StringIO()

        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
                "dict": dict, "divmod": divmod, "enumerate": enumerate,
                "float": float, "int": int, "len": len, "list": list,
                "map": map, "max": max, "min": min, "pow": pow, "print": print,
                "range": range, "reversed": reversed, "round": round, "set": set,
                "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
                "zip": zip, "True": True, "False": False, "None": None,
                "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
                "ZeroDivisionError": ZeroDivisionError, "IndexError": IndexError, "KeyError": KeyError,
            },
            "math": math,
        }

        try:
            sys.stdout = redirected_output
            sys.stderr = redirected_error
            exec(cleaned_code, safe_globals)
            output = redirected_output.getvalue()
            error = redirected_error.getvalue()

            res = ""
            if output:
                res += output
            if error:
                res += f"\nErrors: {error}"
            return res.strip() or "Code executed successfully with no output."
        except Exception as e:
            return f"Execution Error: {str(e)}\n{traceback.format_exc(limit=2)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
