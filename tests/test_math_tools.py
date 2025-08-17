from mcp_server_openai.tools import math_tools

def test_add_numbers() -> None:
  assert math_tools.add_numbers(2, 3) == 5
  assert math_tools.add_numbers(-1, 1) == 0

def test_subtract_numbers() -> None:
  assert math_tools.subtract_numbers(7, 2) == 5
  assert math_tools.subtract_numbers(0, 5) == -5
