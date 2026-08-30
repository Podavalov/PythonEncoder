import ast

def get_names_from_script(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    variables = set()
    functions = set()
    classes = {}
    methods = set()
    arguments = set()
    loop_vars = set()
    except_vars = set()
    with_vars = set()
    import_aliases = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.add(target.id)
        elif isinstance(node, ast.FunctionDef):
            functions.add(node.name)
            for arg in node.args.args:
                arguments.add(arg.arg)
            if node.args.vararg:
                arguments.add(node.args.vararg.arg)
            if node.args.kwarg:
                arguments.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            classes[class_name] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    classes[class_name].append(item.name)
                    methods.add(f"{class_name}.{item.name}")
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                loop_vars.add(node.target.id)
        elif isinstance(node, ast.comprehension):
            if isinstance(node.target, ast.Name):
                loop_vars.add(node.target.id)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                except_vars.add(node.name)
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                    with_vars.add(item.optional_vars.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                import_aliases.add(alias.name)
                if alias.asname:
                    import_aliases.add(alias.asname)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                import_aliases.add(alias.name)
                if alias.asname:
                    import_aliases.add(alias.asname)

    all_defs = set()
    all_defs.update(variables)
    all_defs.update(functions)
    all_defs.update(classes.keys())
    all_defs.update(arguments)
    all_defs.update(loop_vars)
    all_defs.update(except_vars)
    all_defs.update(with_vars)
    all_defs.update(import_aliases)
    for m in methods:
        simple = m.split('.')[-1]
        all_defs.add(simple)

    return {
        'variables': list(variables),
        'functions': list(functions),
        'classes': classes,
        'methods': list(methods),
        'all_definitions': list(all_defs)
    }