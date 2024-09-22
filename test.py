import unittest
from str_graph_cpp import DAG


class TestStrGraphCpp(unittest.TestCase):

    def test_basic(self):
        dag = DAG()
        self.assertEqual(len(dag.get_nodes_values()), 0)

        dag.set_const_node(0, "aaaa")
        dag.set_const_node(1, "aaa")
        dag.set_const_node(2, "bbb")
        dag.set_calc_node(3, "replace", [0, 1, 2])
        dag.set_const_node(4, "123")
        dag.set_calc_node(5, "concat", [3, 4], is_result=True)
        self.assertEqual(len(dag.get_nodes_values()), 6)
        self.assertEqual(
            dag.get_nodes_values(),
            {0: "aaaa", 1: "aaa", 2: "bbb", 3: None, 4: "123", 5: None},
        )

        result = dag.execute()
        self.assertEqual(result, "bbba123")
        self.assertEqual(len(dag.get_nodes_values()), 6)
        self.assertEqual(
            dag.get_nodes_values(),
            {0: "aaaa", 1: "aaa", 2: "bbb", 3: "bbba", 4: "123", 5: "bbba123"},
        )

    def test_empty_dag(self):
        dag = DAG()
        self.assertEqual(len(dag.get_nodes_values()), 0)

        result = dag.execute()
        self.assertIsNone(result)
        self.assertEqual(len(dag.get_nodes_values()), 0)

    def test_only_consts(self):
        dag = DAG()
        dag.set_const_node(1, "aaa")
        dag.set_const_node(2, "bbb")
        self.assertEqual(len(dag.get_nodes_values()), 2)
        self.assertEqual(
            dag.get_nodes_values(),
            {1: "aaa", 2: "bbb"},
        )

        result = dag.execute()
        self.assertIsNone(result)
        self.assertEqual(len(dag.get_nodes_values()), 2)
        self.assertEqual(
            dag.get_nodes_values(),
            {1: "aaa", 2: "bbb"},
        )

    def test_result_value(self):
        dag = DAG()
        dag.set_const_node(1, "aaa")
        dag.set_const_node(2, "bbb")
        dag.set_calc_node(3, "concat", [1, 2])
        result = dag.execute()
        self.assertIsNone(result)

        dag.set_calc_node(3, "concat", [1, 2], is_result=True)
        result = dag.execute()
        self.assertEqual(result, "aaabbb")

    def test_operations(self):
        dag = DAG()
        dag.set_const_node(0, "aBc")
        dag.set_calc_node(1, "capitalize", [0])
        dag.set_calc_node(2, "lower", [0])
        dag.set_calc_node(3, "upper", [0])
        result = dag.execute()
        self.assertIsNone(result)
        self.assertEqual(
            dag.get_nodes_values(),
            {
                0: "aBc",
                1: "Abc",
                2: "abc",
                3: "ABC",
            },
        )

        dag.set_const_node(5, "ababab")
        dag.set_const_node(6, "a")
        dag.set_const_node(7, "cc")
        dag.set_calc_node(8, "replace", [5, 6, 7])
        result = dag.execute()
        self.assertIsNone(result)
        self.assertEqual(dag.get_nodes_values()[8], "ccbccbccb")

    def test_setup_graph_from_function(self):
        dag = DAG()

        def f(s1, s2):
            for i in range(5):
                s1 += s2
            s = s1.replace("b", "c")
            return s

        dag.setup_graph_from_function(f, ["a", "b"])
        self.assertEqual(
            dag.get_nodes_values(),
            {
                0: "a",
                1: "b",
                2: None,
                3: None,
                4: None,
                5: None,
                6: None,
                7: None,
                8: "b",
                9: "c",
            },
        )

        result = dag.execute()
        self.assertEqual(
            dag.get_nodes_values(),
            {
                0: "a",
                1: "b",
                2: "ab",
                3: "abb",
                4: "abbb",
                5: "abbbb",
                6: "abbbbb",
                7: "accccc",
                8: "b",
                9: "c",
            },
        )
        self.assertEqual(result, "accccc")

    def test_setup_graph_from_function_swap(self):
        dag = DAG()

        def f(s1, s2):
            s1, s2 = s2, s1
            return s1 + s2

        dag.setup_graph_from_function(f, ["a", "b"])
        result = dag.execute()
        self.assertEqual(result, "ba")

    def test_setup_graph_from_function_wrong_return_type_should_fail(self):
        dag = DAG()

        def f(s1, s2):
            s = s1 + s2
            return 123

        with self.assertRaises(Exception):
            dag.setup_graph_from_function(f, ["a", "b"])

        def f(s1, s2):
            s = s1 + s2
            return None

        with self.assertRaises(Exception):
            dag.setup_graph_from_function(f, ["a", "b"])

    def test_setup_graph_from_functionJ_with_wrong_param_values_should_fail(self):
        dag = DAG()

        def f(s1, s2):
            for i in range(5):
                s1 += s2
            s = s1.replace("b", "c")
            return s

        with self.assertRaises(TypeError):
            dag.setup_graph_from_function(f, ["a", "b", "c"])

    def test_dag_with_cycle_should_fail(self):
        dag = DAG()
        dag.set_const_node(0, "aaa")
        dag.set_calc_node(2, "concat", [0, 3])
        dag.set_calc_node(3, "concat", [0, 2])
        with self.assertRaises(Exception):
            dag.execute()

    def test_dag_with_cycle_should_fail_2(self):
        dag = DAG()
        dag.set_const_node(0, "aaaa")
        dag.set_calc_node(1, "concat", [0, 1])
        with self.assertRaises(Exception):
            dag.execute()

    def test_dag_with_undefined_nodes_should_fail(self):
        dag = DAG()
        dag.set_const_node(0, "aaaa")
        dag.set_calc_node(1, "concat", [0, 2])
        with self.assertRaises(Exception):
            dag.execute()

    def test_operation_wrong_parameters_should_fail(self):
        dag = DAG()
        dag.set_const_node(0, "aaaa")
        dag.set_const_node(1, "aaaa")
        dag.set_calc_node(2, "replace", [0, 1])
        with self.assertRaises(Exception):
            dag.execute()


if __name__ == "__main__":
    unittest.main()
