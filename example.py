# Below is a simple example on how to use the str_graph_cpp library.

from str_graph_cpp import DAG

# There are two methods to create a dag: through node setters or through a function

## Method 1: Set up graph using node setters

dag = DAG()
dag.set_const_node(0, "hello ")
dag.set_const_node(1, "world ")
dag.set_calc_node(3, "concat", [0, 1])
dag.set_const_node(4, "o")
dag.set_const_node(5, "ooo")
dag.set_calc_node(6, "replace", [3, 4, 5])
dag.set_calc_node(7, "upper", [6])
dag.set_calc_node(8, "concat", [7, 3])

# This is an operation not supported in CPP engine, so Python engine will be used.
dag.set_calc_node(9, "capitalize", [8], is_result=True)
result = dag.execute()
print(dag)


## Method 2: Set up graph using function


def f(s1, s2):
    for i in range(10):
        s1 += s2
    s = s1.replace("o", "ooo")
    return s


dag.setup_graph_from_function(f, ["hello ", "world "])
result = dag.execute()
print(dag)
