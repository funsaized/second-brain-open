#!/usr/bin/env python3
"""Read-only statistics for an owner-approved, frozen managed wiki.

Usage: python3 scripts/vault_stats.py VAULT [--json] [--as-of YYYY-MM-DD]
No model calls, repairs or metrics-note writes. Real reports can contain private
paths: keep them local. These counts describe structure, not factual quality.
"""

import argparse
from datetime import date
import json
import sys

if __package__:
    from . import link_check
else:
    import link_check


DEFINITIONS = {
    "pages": "N: Markdown files in the adopted content folders, including malformed pages; controls/instructions excluded.",
    "by_type": "Recognized leading-frontmatter type; absent, invalid or ambiguous types are unknown. Folder mismatches remain diagnostics.",
    "resolved_links": "E: unique directed non-self edges between canonical in-scope page paths; no basename or alias guessing.",
    "average_out_degree": "E/N; null when N=0.",
    "average_total_degree": "2E/N; null when N=0.",
    "inbound_orphans": "Pages with zero incoming content edges; rate=count/N, null when N=0.",
    "weak_components": "Connected components after ignoring edge direction; largest_share=largest_size/N, null when N=0.",
    "stale_concepts": "Declared concepts with (as_of-updated)>90 days. Rate=count/eligible; eligible requires a valid non-future date. Unknown=total-eligible; null rate if no eligible concepts.",
    "update_dates": "Disjoint counts over N: valid non-future, missing (absent/null), invalid, future. Invalid JSON or duplicate updated fields are invalid, never eligible.",
    "most_linked": "Up to ten pages with positive unique inbound counts, descending count then canonical path.",
    "diagnostics": "Inherited metadata/link findings. Excluded control targets are not inspected; fragment anchors remain unchecked. Use link_check for validation exit status.",
}


def iso_date(value):
    if not isinstance(value, str) or not link_check.ISO.fullmatch(value):
        raise ValueError("expected YYYY-MM-DD")
    return date.fromisoformat(value)


def report(vault, as_of):
    pages, metadata_issues = link_check.collect(vault, include_controls=False)
    edges, link_issues = link_check.resolve_links(pages, include_controls=False)
    by_type = dict.fromkeys(sorted([*link_check.FOLDERS.values(), "unknown"]), 0)
    update_dates = dict.fromkeys(("valid", "missing", "invalid", "future"), 0)
    stale = {"total": 0, "eligible": 0, "unknown": 0, "count": 0, "rate": None, "threshold_days": 90}

    # The parser preserves fields for diagnosis; an ambiguous field must not make
    # a page look fresh merely because its first parseable value was a valid date.
    ambiguous = {path: set() for path in pages}
    for issue in metadata_issues:
        if issue.get("unusable_field") in ("type", "updated"):
            ambiguous[issue["page"]].add(issue["unusable_field"])

    for path, page in pages.items():
        fields = page["metadata"]
        kind = fields.get("type")
        if not isinstance(kind, str) or kind not in by_type or "type" in ambiguous[path]:
            kind = "unknown"
        by_type[kind] += 1
        updated = fields.get("updated")
        parsed = None
        if "updated" in ambiguous[path]:
            status = "invalid"
        elif updated is None:
            status = "missing"
        else:
            try:
                parsed = iso_date(updated)
                status = "future" if parsed > as_of else "valid"
            except ValueError:
                status = "invalid"
        update_dates[status] += 1
        if kind == "concept":
            stale["total"] += 1
            if status == "valid":
                stale["eligible"] += 1
                stale["count"] += (as_of - parsed).days > 90
            else:
                stale["unknown"] += 1
    if stale["eligible"]:
        stale["rate"] = stale["count"] / stale["eligible"]

    inbound = dict.fromkeys(pages, 0)
    neighbors = {path: set() for path in pages}
    for source, target in edges:
        inbound[target] += 1
        neighbors[source].add(target)
        neighbors[target].add(source)
    remaining = set(pages)
    component_count = largest = 0
    while remaining:
        pending = [remaining.pop()]
        size = 0
        while pending:
            current = pending.pop()
            size += 1
            unseen = neighbors[current] & remaining
            remaining.difference_update(unseen)
            pending.extend(unseen)
        component_count += 1
        largest = max(largest, size)

    nodes, links = len(pages), len(edges)
    orphan_count = sum(count == 0 for count in inbound.values())
    ranked = sorted((path for path in pages if inbound[path]), key=lambda path: (-inbound[path], path))[:10]
    diagnostics = sorted(metadata_issues + link_issues, key=lambda item: (
        item["page"], item.get("line", 0), item["kind"], item.get("target", ""), item.get("detail", ""),
    ))
    return {
        "schema_version": 1,
        "as_of": as_of.isoformat(),
        "scope": {"folders": sorted(f"wiki/{folder}" for folder in link_check.FOLDERS),
                  "excluded_controls": list(link_check.CONTROLS),
                  "excluded_instruction_names": sorted(link_check.INSTRUCTIONS),
                  "other_vault_folders": "not scanned", "control_targets": "not inspected"},
        "definitions": DEFINITIONS.copy(),
        "pages": nodes,
        "by_type": by_type,
        "resolved_links": links,
        "average_out_degree": links / nodes if nodes else None,
        "average_total_degree": 2 * links / nodes if nodes else None,
        "inbound_orphans": {"count": orphan_count, "rate": orphan_count / nodes if nodes else None},
        "weak_components": {"count": component_count, "largest_size": largest,
                            "largest_share": largest / nodes if nodes else None},
        "stale_concepts": stale,
        "update_dates": update_dates,
        "most_linked": [{"path": path, "inbound": inbound[path]} for path in ranked],
        "diagnostics": diagnostics,
    }


def human_report(result):
    def percent(value):
        return "n/a" if value is None else f"{value:.2%}"

    print(f"Managed wiki statistics (definitions v{result['schema_version']}, as of {result['as_of']})")
    print("Scope: " + ", ".join(result["scope"]["folders"]))
    print(f"Pages: {result['pages']}; types: " + ", ".join(f"{key}={value}" for key, value in result["by_type"].items()))
    print(f"Unique directed links: {result['resolved_links']}")
    for key, label in (("average_out_degree", "Average out-degree E/N"),
                       ("average_total_degree", "Average total directed degree 2E/N")):
        value = result[key]
        print(f"{label}: {'n/a' if value is None else f'{value:.4f}'}")
    orphans, components, stale = result["inbound_orphans"], result["weak_components"], result["stale_concepts"]
    print(f"Inbound orphans: {orphans['count']}/{result['pages']} ({percent(orphans['rate'])})")
    print(f"Weak components: {components['count']}; largest: {components['largest_size']}/{result['pages']} ({percent(components['largest_share'])})")
    print(f"Stale concepts (>90 days): {stale['count']}/{stale['eligible']} eligible ({percent(stale['rate'])}); total={stale['total']}, unknown={stale['unknown']}")
    print("Update dates: " + ", ".join(f"{key}={value}" for key, value in result["update_dates"].items()))
    print("Most linked (unique inbound):")
    for item in result["most_linked"]:
        print(f"  {item['inbound']:>4}  {item['path']}")
    print(f"Diagnostics: {len(result['diagnostics'])} (report only; not repaired)")
    for item in result["diagnostics"]:
        print(f"  {item}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", help="approved real directory containing wiki/ (missing wiki means empty)")
    parser.add_argument("--json", action="store_true", help="deterministic report including scope and definitions")
    parser.add_argument("--as-of", type=iso_date, default=date.today(), metavar="YYYY-MM-DD",
                        help="report date; defaults to the operator's local date")
    args = parser.parse_args()
    try:
        result = report(args.vault, as_of=args.as_of)
    except (ValueError, OSError) as error:
        parser.exit(2, f"invalid scope: {error}\n")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    else:
        human_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
