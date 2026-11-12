from agents.echo.graph import graph


def test_graph_runs_both_nodes_in_order():
    out = graph.invoke({"text": "  xin   chào  "})
    assert out["normalized"] == "xin chào"
    assert out["reply"] == "Echo: xin chào"
    # reducer operator.add nối các bước, không ghi đè
    assert out["steps"] == ["normalize", "respond"]


def test_empty_input():
    assert graph.invoke({"text": "   "})["reply"] == "Echo: (tin nhắn rỗng)"
