from graphlib import TopologicalSorter, CycleError
from enum import Enum
import CPPEngine  # type: ignore
import inspect


class _PythonEngine:
    @staticmethod
    def __str__():
        return "Python Engine"

    @staticmethod
    def concat(s1, s2):
        return s1 + s2

    @staticmethod
    def execute(operation, *args):
        if hasattr(_PythonEngine, operation):
            f = getattr(_PythonEngine, operation)
            return f(*args)
        else:
            # This is the catch-all execution for all python str operations.
            s = args[0]
            assert hasattr(s, operation)
            f = getattr(s, operation)
            return f(*args[1:])


class DAG:
    """
    This class represents a DAG that contains string operations. The DAG can be constructed
    using the following node manipulation methods.

    A node in the DAG can be either a CONST node or a CALC node. A CONST node contains a
    constant string. A CALC node is calculated during execution from other nodes.

    Call info() at any time to get overview of the graph.

    Call execute() to execute the graph. Whenever an operation is provided by the CPP engine,
    it will be executed using the CPP engine, otherwise the Python engine will be used.
    """

    @staticmethod
    def get_supported_operations():
        """
        Returns the list of supported operations.
        """
        return [i for i in CPPEngine.__dir__() if not i.startswith("__")]

    class _Node:
        # Representation of a DAG Node. Users are not expected to directly modify it.

        class _NodeType(Enum):
            CONST = 1
            CALC = 2

        def __init__(self, dag, index, node_type, value, operation, children=[]):
            self.dag = dag
            self.index = index
            self.type = node_type
            self.value = value
            self.operation = operation
            self.children = children

        def __str__(self):
            if self.type is self._NodeType.CONST:
                return f"CONST: {self.value}"
            else:
                return f"CALC: operation: {self.operation}, children: {self.children}, value: {self.value}"

        def __add__(self, s):
            return self.dag._create_node(
                None, self._NodeType.CALC, None, "concat", [self, s]
            )

        def __getattribute__(self, name):
            if name in DAG.get_supported_operations():

                def f(*args):
                    return self.dag._create_node(
                        None, self._NodeType.CALC, None, name, [self, *args]
                    )

                return f
            else:
                return object.__getattribute__(self, name)

    def __init__(self):
        self._nodes = {}  # key: index, value: Node object
        self._sorted = (
            True  # Whether self._order contains valid topologically sorted nodes
        )
        self._order = []  # Used to store topological sort result
        self._result_node = None  # The node that's designated as the result

    def _create_node(self, index, node_type, value, operation, children):
        if index is None:
            index = len(self._nodes)
            while index in self._nodes:
                index += 1
        self._nodes[index] = (
            None  # Take the spot now in case new const nodes are created later.
        )

        # Since we support setting up graph using function, children can be one of:
        #  - an index
        #  - a value (string)
        #  - a node
        # We normalize to storing the index.
        for i, v in enumerate(children):
            if isinstance(v, self._Node):
                children[i] = v.index
            elif isinstance(v, str):
                node = self._create_node(None, self._Node._NodeType.CONST, v, None, [])
                children[i] = node.index

        self._nodes[index] = self._Node(
            self, index, node_type, value, operation, children
        )
        self._sorted = False
        return self._nodes[index]

    def set_const_node(self, index, value):
        """
        Sets up a node containing constant value.

        Args:

            index(int): The index of the node.
            value(str): The value of the node.

        Returns:
            None

        Raises:
            TypeError: Input types are wrong.
        """
        if not isinstance(index, int):
            raise TypeError("index should be int.")
        if not isinstance(value, str):
            raise TypeError("value should be str.")

        self._create_node(index, self._Node._NodeType.CONST, value, None, [])

    def set_calc_node(self, index, operation, children, is_result=False):
        """
        Sets up a node of which the value will be calculated. The value will be calculated using
        the given operation and using the children nodes values as input.

        Args:

            index(int): The index of the node.
            operation(str): The operation, can be one of the following values or other Python str members that returns a string

            - concat
            - upper
            - lower
            - replace
            - Any other Python str member that returns a string
                  https://docs.python.org/3/library/stdtypes.html#string-methods

            children(list of int): The children of the node.
            is_result: If True, designate the node as the result.

        Returns:
            None

        Raises:
            TypeError: Input types are wrong.
        """
        if not isinstance(index, int):
            raise TypeError("index should be int.")
        if not isinstance(operation, str):
            raise TypeError("operation should be str.")
        if not isinstance(children, list) or not all(
            isinstance(i, int) for i in children
        ):
            raise TypeError("children should be list of int.")

        self._create_node(index, self._Node._NodeType.CALC, None, operation, children)
        if is_result:
            self._result_node = self._nodes[index]

    def setup_graph_from_function(self, f, param_values):
        """
        Sets up the graph using the given function f and the parameter values.

        The DAG nodes will be generated using the calculation logic of f and with param_values as input values.

        Features supported in function:

            variable assignment
            +: addition is treated as string concat.
            string operations: see set_calc_node() for the type of operations supported.
            loop: loop will be expanded in the graph.
            conditions: note while this method can accept functions with conditions, the final generated dag won't have conditions,
                therefore users shouldn't modified values afterwards using set_const_nodes and expect the conditions to take effect.

        Args:

            f(callable): The function used to used setup the graph.
            param_values(list of str): A list of string values to be passed to f.

        Raises:

            TypeError: Input types are wrong or number of params are wrong.
            Exception: f return type error.
        """
        if not callable(f):
            raise TypeError("f should be a function.")
        if not isinstance(param_values, list) or not all(
            isinstance(i, str) for i in param_values
        ):
            raise TypeError("param_values should be list of str.")
        if len(inspect.signature(f).parameters) != len(param_values):
            raise TypeError(
                "param_values should be of same length as f's parameter list."
            )

        self._nodes.clear()
        inputs = [
            self._create_node(None, self._Node._NodeType.CONST, value, None, [])
            for value in param_values
        ]

        result_node = f(*inputs)
        if not result_node or not isinstance(result_node, DAG._Node):
            raise Exception("f return value type error.")
        self._result_node = result_node

    def delete_node(self, index):
        """
        Deletes a node.

        Args:

            index(int): The index of the node.

        Returns:
            None

        Raises:
            TypeError: Input types are wrong.
        """
        if not isinstance(index, int):
            raise TypeError("index should be int.")

        if self._result_node is self._nodes[index]:
            self._result_node = None
        del self._nodes[index]
        self._sorted = False

    def get_nodes_values(self):
        """
        Returns the result dictionary, where the keys are the node indexes and the values are the values of the nodes.
        """
        return {i: v.value for i, v in self._nodes.items()}

    def _execute_node(self, index, node, force_python_engine=False, verbose=False):
        assert node.type is self._Node._NodeType.CALC

        # Use the CPP engine when not forcing python engine and the operation is supported.
        use_cpp_engine = force_python_engine is False and hasattr(
            CPPEngine, node.operation
        )

        params = [self._nodes[i].value for i in node.children]
        if verbose:
            print(
                f"Calculating node {index} using {'CPP' if use_cpp_engine else 'Python'} engine: {node.operation}, {params}"
            )

        if use_cpp_engine:
            f = getattr(CPPEngine, node.operation)
            result = f(*params)
        else:
            f = _PythonEngine.execute
            result = f(node.operation, *params)
        assert isinstance(result, str)

        if verbose:
            print(f" Result: {result}")
        return result

    def execute(self, force_python_engine=False, verbose=False):
        """
        Executes the graph, prepares the graph and checks for potential cycles and undefined nodes.

        Args:

            force_python_engine(bool): If True, force the execution to use the Python engine.
                Otherwise use the CPP Engine when the operation is supported, fall back to the Python engine when necessary.
            verbose(bool): If True, prints the details for each step of the execution.

        Returns:
            The value of the result node if there is one, None if not.

        Raises:
            Exception: If the execution encounters any issue. See exception detail or turn on verbose parameter to see the details.
        """

        try:
            self._prepare()
        except CycleError:
            if verbose:
                print("Nodes in the graph have cycle.")
            raise Exception("Nodes in the graph have cycle.")

        for i in self._order:
            if i not in self._nodes:
                if verbose:
                    print(f"Node {i} is undefined.")
                raise Exception(f"Node {i} is undefined.")
            node = self._nodes[i]
            if node.type is self._Node._NodeType.CALC:
                try:
                    node.value = self._execute_node(
                        i, node, force_python_engine, verbose
                    )
                except Exception as e:
                    if verbose:
                        print(f"Node {i} execution failed. Wrong parameters?")
                        print(e)
                    raise Exception(f"Node {i} execution failed.")
                if not isinstance(node.value, str):
                    if verbose:
                        print(f"Node {i} generated value that is not str.")
                    raise Exception(f"Node {i} generated value that is not str.")
        return self._result_node.value if self._result_node is not None else None

    def _prepare(self):
        if not self._sorted:
            graph = {i: set(node.children) for i, node in self._nodes.items()}
            ts = TopologicalSorter(graph)
            self._order = list(ts.static_order())
            self._sorted = True

    def info(self):
        """
        Returns the info string of the DAG.
        """
        result = f"""  DAG INFO
-------------
CPPEngine supports: {', '.join(DAG.get_supported_operations())}
Nodes: {len(self._nodes)}
"""
        for i, node in self._nodes.items():
            result += f"{i}: {node}\n"
        if self._result_node:
            result += f"result: {self._result_node.value}"
        return result

    def __str__(self):
        return self.info()
