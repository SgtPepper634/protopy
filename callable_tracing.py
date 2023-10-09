import inspect
from shared_types import MethodList
from protocols import write_protocols

def is_user_defined_method(method) -> bool:
  return inspect.isroutine(method) and not inspect.isbuiltin(method) # TODO: handle decorator functions

def print_custom_methods(methods: MethodList, parent) -> None:
  if len(methods) > 0:
    print(f"\t{parent} user-defined methods:")
    for method in methods:
      print(f'\t\t{method}')
    print('\n')

def get_arguments_user_defined_methods(arg_value) -> MethodList:
  custom_methods = [method for method in inspect.getmembers(arg_value) if is_user_defined_method(method[1])] 
  print_custom_methods(custom_methods, arg_value)
  return custom_methods


# local trace function which returns itself
def callable_tracer(frame, event, arg = None): 
  # https://www.geeksforgeeks.org/python-sys-settrace/
  # https://docs.python.org/3/library/inspect.html
  # https://docs.python.org/3/library/sys.html#sys.settrace

  # extracts the line number where the function was called
  line_no = frame.f_back.f_lineno
  # extracts frame code 
  code = frame.f_code 
  # extracts name of function that was called 
  func_name = code.co_name 
  # extracts argument count
  arg_count = code.co_argcount
  # extracts argument and local variable names
  arg_names = code.co_varnames
  
  custom_methods = None

  if event == 'call':
    # arg parameter is always None here 
    print(f"Function CALL: line number {line_no}:") 
    print(f"\tfunction name  = {func_name}")
    print(f"\targument count = {arg_count}\n")

    # code.co_varnames includes local variables so must use range to only iterate through arguments
    for i in range(arg_count): 
      arg_name = arg_names[i]

      if arg_name == 'self':
        continue

      arg_value = frame.f_locals[arg_name]

      print(f"\targument name  = {arg_name} ")
      print(f"\targument value = {arg_value}")
      print(f"\targument type  = {type(arg_value)}\n")
    
      custom_methods = get_arguments_user_defined_methods(arg_value)

  elif event == 'return':
    print(f"Function RETURN: line number {line_no}:") 
    print(f"\tfunction name = {func_name}")
    print(f"\treturn value  = {arg}")
    print(f"\treturn type   = {type(arg)}\n")  

    custom_methods = get_arguments_user_defined_methods(arg)

  elif event == 'line':
    return
  
  write_protocols(custom_methods)

  return callable_tracer
