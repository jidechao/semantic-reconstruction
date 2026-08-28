"""Risk-term detector for context dependencies."""
from __future__ import annotations

from .models import Evidence

HIGH_RISK_TERMS: dict[str, str] = {
    "上述": "前文指代",
    "以上": "前文指代",
    "以下": "后文或本段指代",
    "本办法": "制度范围指代",
    "本产品": "对象指代",
    "该客户": "对象指代",
    "这种情况": "条件指代",
    "如下图所示": "图片指代",
    "下图": "图片指代",
    "下表": "表格指代",
    "按下表执行": "表格指代",
    "右侧": "版式位置指代",
    "附件": "附件引用",
    "除外": "例外边界",
    "但不": "例外边界",
    "仅限": "限制条件",
    "不得": "禁止性规则",
    "原则上": "确定性约束",
    "另行": "外部规则引用",
    "以最新通知为准": "版本依赖",
}

ROLE_TERMS = (
    "申请人", "负责人", "总监", "财务", "系统", "管理员", "专员", "部门", "区域", "客户", "用户", "开发者",
)


def detect_risk_flags(evidence: list[Evidence]) -> list[str]:
    flags: list[str] = []
    for item in evidence:
        for term, dependency in HIGH_RISK_TERMS.items():
            flag = f"{dependency}：{term}"
            if term in item.text and flag not in flags:
                flags.append(flag)
    return flags


def has_explicit_role(text: str) -> bool:
    return any(role in text for role in ROLE_TERMS)
