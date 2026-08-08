import json

def _json_default(o):
    # numpy 数组 / 标量 -> 原生 Python 类型
    if hasattr(o, "tolist"):
        return o.tolist()
    # scipy 稀疏矩阵(csr) -> {token_id: weight}
    if hasattr(o, "indices") and hasattr(o, "data"):
        return {int(i): float(w) for i, w in zip(o.indices, o.data)}
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

def json_tool(data):
    return json.dumps(data, indent=4, ensure_ascii=False, default=_json_default)