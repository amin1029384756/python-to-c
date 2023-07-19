import ast
import os
import sys
import requests
import astunparse

class CFunction:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def to_c(self):
        c_definition = 'void ' + self.name + '('
        c_definition += ', '.join(['int ' + arg.arg for arg in self.args.args])
        c_definition += ') {\n'
        for index in range(len(self.body)):
            if isinstance(self.body[index], CAssign):
                c_definition += '    ' + (self.body[index]).to_c() + '\n'
        c_definition += '}\n'
        return c_definition

class CAssign:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_c(self):
        return 'int ' + self.name + ' = ' + str(self.value) + ';'

class CClass:
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def to_c(self):
        c_definition = 'struct ' + self.name + ' {\n'
        for index in range(len(self.body)):
            if isinstance(self.body[index], CAssign):
                c_definition += '    ' + (self.body[index]).to_c() + '\n'
        c_definition += '};\n'
        return c_definition

class CodeExtractor(ast.NodeVisitor):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.ignore)
        return visitor(node)

    def ignore(self, node):
        pass

    def visit_Assign(self, node):
        name = node.targets[0].id
        value = node.value.n
        return CAssign(name, value)

    def visit_FunctionDef(self, node):
        name = node.name
        args = node.args
        body = [self.visit(statement) for statement in node.body]
        return CFunction(name, args, body)

    def visit_ClassDef(self, node):
        name = node.name
        body = [self.visit(statement) for statement in node.body]
        return CClass(name, body)

def extract_code(python_code):
    python_ast = ast.parse(python_code)
    extractor = CodeExtractor()
    c_code = ''
    for node in python_ast.body:
        c_code += extractor.visit(node).to_c() + '\n'
    return c_code

def translate_file(file_path):
    with open(file_path, 'r') as file:
        python_code = file.read()
    c_code = extract_code(python_code)
    c_file_path = file_path.replace('.py', '.c')
    with open(c_file_path, 'w') as file:
        file.write(c_code)

def translate_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                translate_file(file_path)

def main():
    directory = sys.argv[1]
    translate_directory(directory)

if __name__ == '__main__':
    main()
