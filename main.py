import os
import glob
import re
import networkx as nx


class Tf_deploy_preprocessor:

    def __init__(self, modules_path):
        self.errors = []
        self.deploy_order = []
        dependencies_graph = self.create_dependencies_graph(modules_path)
        print(f'Dependency graph:\n{dependencies_graph}\n')
        dependencies_graph = self.remove_excluded_modules(dependencies_graph)
        self.validate(dependencies_graph)
        if self.errors:
            print('Errors:')
            print('\n'.join(self.errors))
        else:
            self.deploy_order = self.get_modules_deploy_order(dependencies_graph)
            print(f'Deploy order:\n{self.deploy_order}\n')

    def create_dependencies_graph(self, modules_path):
        graph = {}
        modules = next(os.walk(modules_path))[1]
        for module in modules:
            graph[module] = []
            module_path = os.path.join(modules_path, module)
            for filepath in glob.glob(os.path.join(module_path, '*.tf')):
                data = self.read_file(filepath)
                graph[module] += self.find_tf_dependencies(data)
        return graph

    def find_tf_dependencies(self, data):
        dependencies = []
        results = re.findall(r'join\(\"/\", compact\(\[\"terraform-state\", \"(.*)\".*\]\)\)', data)
        for result in results:
            dependencies.append(result)
        return dependencies

    def read_file(self, filepath):
        with open(filepath, 'r') as in_file:
            return in_file.read()

    def get_modules_deploy_order(self, dependencies_graph):
        graph = nx.DiGraph(dependencies_graph)
        return list(reversed(list(nx.topological_sort(graph))))

    def remove_excluded_modules(self, dependencies_graph):
        excluded = []  # TODO read data from .deployignore file
        for module in excluded:
            try:
                del dependencies_graph[module]
            except KeyError:
                self.errors.append(f'{module} is not a valid module name.')
        return dependencies_graph

    def validate(self, dependencies_graph):
        for module, dependencies in dependencies_graph.items():
            for dependency in dependencies:
                if dependency not in dependencies_graph:
                    msg = f'Module {dependency} is required by {module} but was not found in the modules to be deployed'
                    self.errors.append(msg)


if __name__ == '__main__':
    path = <PATH TO TERRAFORM FOLDER>
    deploy_order = Tf_deploy_preprocessor(path).deploy_order
