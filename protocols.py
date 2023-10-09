from shared_types import MethodList

def generate_protocol_name(class_name: str, method_name: str) -> str:  
  return f'{class_name}_{"".join([name_component[0].upper() + name_component[1:] for name_component in method_name.split("_")])}'

def write_protocols(method_list: MethodList) -> None:
  with open('main.py', 'a+') as file: # TODO: Write Protocols in the proper file
    for method_name, method in method_list:
      class_name = method.__self__.__class__.__name__
      protocol_name = generate_protocol_name(class_name, method_name)
      
      file.write(f'''
@runtime_checkable
class {protocol_name}(Protocol):
  def {method_name}(self):
    ...
''')
      
    file.close()