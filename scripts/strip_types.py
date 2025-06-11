import ast
import astor
import tomllib
import shutil
import os
import glob


# https://stackoverflow.com/a/61308385
class TypeHintRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # remove the return type definition
        node.returns = None
        # remove all argument annotations
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        if node.value is None:
            return None
        return ast.Assign([node.target], node.value)

    # def visit_Import(self, node):
    #     node.names = [n for n in node.names if n.name != "typing"]
    #     return node if node.names else None

    # def visit_ImportFrom(self, node):
    #     return node if node.module != "typing" else None


def remove_types(content: str) -> str:
    # parse the source code into an AST
    parsed_source = ast.parse(content)
    # remove all type annotations, function return type definitions
    # and import statements from 'typing'
    transformed = TypeHintRemover().visit(parsed_source)
    # convert the AST back to source code
    return astor.to_source(transformed)


with open("build.toml", "rb") as filein:
    build = tomllib.load(filein)

    src_path = os.path.join(os.getcwd(), build["src"])
    dest_path = os.path.join(os.getcwd(), build["dest"])

    shutil.rmtree(dest_path, ignore_errors=True)
    shutil.copytree(src_path, dest_path)

    python_files = glob.glob(f"{dest_path}/**/*.py", recursive=True)

    for filename in python_files:
        with open(filename, "r") as filein:
            content = "".join(filein.readlines())

            with open(filename, "w") as fileout:
                fileout.write(remove_types(content))
