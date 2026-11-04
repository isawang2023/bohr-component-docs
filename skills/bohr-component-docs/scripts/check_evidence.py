#!/usr/bin/env python3
"""Check evidence records, not the truth or completeness of design observations."""
import hashlib
import json
from pathlib import Path
import sys

GROUPS = {"P", "A", "B", "C", "D", "C1", "C2", "E"}
KINDS = {"raw-design", "raw-online"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("checks必须是非空列表")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError("检查项缺少id")
        if row["id"] in result:
            raise ValueError("重复检查项: " + row["id"])
        result[row["id"]] = row
    return result


def validate(contract_path, report_path):
    c = json.loads(contract_path.read_text())
    r = json.loads(report_path.read_text())
    if not isinstance(c, dict) or not isinstance(r, dict):
        raise ValueError("输入必须为对象")
    expected, results = index(c.get("checks")), index(r.get("checks"))
    errors = []
    errors.extend(validate_business_scenarios(c, expected))
    if not c.get("scope"):
        errors.append("缺任务范围")
    refs = c.get("references", [])
    if not isinstance(refs, list) or any(not isinstance(x, dict) for x in refs):
        raise ValueError("references必须为对象列表")
    for role in ("visual", "capability", "online"):
        if not any(x.get("role") == role and (x.get("locator") or x.get("reason")) for x in refs):
            errors.append("缺参照或不适用理由: " + role)
    groups = {x.get("group") for x in expected.values()}
    if groups != GROUPS:
        errors.append("检查分组须覆盖P/A/B/C/D/C1/C2/E，不能省略无关组的理由")
    if not any(x.get("applicable") is True for x in expected.values()):
        errors.append("没有适用检查项")
    if r.get("contract_sha256") != digest(contract_path):
        errors.append("任务清单摘要不匹配")
    if not isinstance(r.get("revision"), str) or not r["revision"].strip():
        errors.append("缺最新产物revision")
    for key in sorted(results.keys() - expected.keys()):
        errors.append(key + ": 结果未在任务清单登记")
    for key, item in expected.items():
        row = results.get(key)
        if not row:
            errors.append(key + ": 缺检查结果")
            continue
        if type(item.get("applicable")) is not bool or not item.get("subject"):
            errors.append(key + ": 缺适用性或源对象")
        if item.get("applicable") is False:
            if not item.get("reason") or row.get("status") != "不适用":
                errors.append(key + ": 不适用缺理由或状态不一致")
            continue
        if row.get("status") != "已通过":
            errors.append(key + ": " + str(row.get("status", "缺状态")))
        if row.get("checked_revision") != r.get("revision"):
            errors.append(key + ": 验收版本过期")
        if not row.get("target") or "actual" not in row or "expected" not in item:
            errors.append(key + ": 缺源预期/目标/实际值")
        method = item.get("method")
        if method == "equal":
            if item.get("expected") != row.get("actual"):
                errors.append(key + ": 实际值与锁定预期不同")
        elif method == "review":
            if not row.get("decision"):
                errors.append(key + ": 缺人工对照结论")
        else:
            errors.append(key + ": 无效检查方法")
        kind = item.get("evidence_kind")
        if kind not in KINDS:
            errors.append(key + ": 无效证据类型")
        evidence = row.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(key + ": 缺原始证据")
            continue
        matched = False
        for e in evidence:
            if not isinstance(e, dict):
                errors.append(key + ": 无效证据条目")
                continue
            if e.get("kind") == kind:
                matched = True
            if not isinstance(e.get("path"), str) or not e["path"] or not e.get("locator"):
                errors.append(key + ": 缺证据路径/定位")
                continue
            path = report_path.parent / e["path"]
            if not path.is_file():
                errors.append(key + ": 证据文件不存在")
            elif e.get("sha256") != digest(path):
                errors.append(key + ": 证据文件摘要不匹配")
        if not matched:
            errors.append(key + ": 原始证据类型不匹配")
    return {"record_check": "未通过" if errors else "通过", "errors": errors,
            "checked_items": len(expected), "component_acceptance": "需结合实际证据人工判定"}


def validate_business_scenarios(contract, checks):
    """Require declared business work to map source, composition and relationships.

    This validates the record graph, not whether its source inventory is truthful.
    Referenced check results still pass through the normal evidence/revision gate.
    """
    deliverables = contract.get("deliverables", [])
    if not isinstance(deliverables, list):
        raise ValueError("deliverables必须为列表")
    if "business-cases" not in deliverables and "business_scenarios" not in contract:
        return []
    scenarios = contract.get("business_scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return ["业务案例缺逐场景business_scenarios记录"]
    errors, seen = [], set()
    if "business-cases" not in deliverables:
        errors.append("业务场景缺business-cases交付类型声明")

    def require_check(key, kind, context, group=None):
        check = checks.get(key) if isinstance(key, str) else None
        if (not check or check.get("applicable") is not True
                or check.get("evidence_kind") != kind
                or (group and check.get("group") != group)):
            errors.append(context + ": 缺适用的" + kind + "检查映射")

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            errors.append("业务场景必须为对象")
            continue
        sid = scenario.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append("业务场景缺id")
            continue
        if sid in seen:
            errors.append(sid + ": 重复场景id，主题副本不是新场景")
        seen.add(sid)
        for field in ("platform", "task"):
            if not isinstance(scenario.get(field), str) or not scenario[field].strip():
                errors.append(sid + ": 缺" + field)
        require_check(scenario.get("source_check"), "raw-online", sid + "/取源", "D")
        require_check(scenario.get("composition_check"), "raw-design", sid + "/整体组合", "C")
        elements = scenario.get("elements")
        if not isinstance(elements, list) or not elements:
            errors.append(sid + ": 缺必要元素清单")
            elements = []
        ids = set()
        for element in elements:
            if not isinstance(element, dict) or not isinstance(element.get("id"), str):
                errors.append(sid + ": 无效元素")
                continue
            eid = element["id"]
            source = element.get("source")
            if (not eid.strip() or eid in ids
                    or not isinstance(source, str) or not source.strip()):
                errors.append(sid + ": 元素缺来源或id重复")
            ids.add(eid)
            require_check(element.get("check"), "raw-design", sid + "/" + eid)
        relations = scenario.get("relations")
        if not isinstance(relations, list) or not relations:
            errors.append(sid + ": 缺必要业务关系")
            relations = []
        for relation in relations:
            if not isinstance(relation, dict):
                errors.append(sid + ": 无效业务关系")
                continue
            endpoints = (relation.get("from"), relation.get("to"))
            if any(not isinstance(x, str) or x not in ids for x in endpoints):
                errors.append(sid + ": 业务关系端点未登记")
            require_check(relation.get("check"), "raw-design", sid + "/关系")
    return errors


def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError("用法: check_evidence.py contract.json report.json")
        result = validate(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"record_check": "输入无效", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
