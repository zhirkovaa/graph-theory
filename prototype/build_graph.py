#!/usr/bin/env python3
"""Build the unified graph (Nodes + Edges) from CE and BC extracts.

Reads prototype/data/*.csv (see generate_sample_data.py), produces:

  prototype/output/nodes.csv  - one row per entity of either system, with
                                node_type, source_system, search_text,
                                materialized path to the account, depth,
                                and an is_orphan data-quality flag;
  prototype/output/edges.csv  - one row per relation (edge_type).

These two tables are exactly what the Power BI report consumes.

Also a CLI demo of the search scenario:

  python3 build_graph.py --search "SN-100234" [--depth 2]

finds nodes matching the query and prints their BFS neighborhood -
the same traversal a report page or a Python visual would run.

No dependencies: standard library only.
"""

import argparse
import csv
from collections import deque
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "output"


def read(name: str) -> list[dict]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build() -> tuple[dict[str, dict], list[dict]]:
    """Return (nodes by id, edges). Edge direction: parent -> child."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_node(node_id: str, node_type: str, label: str, system: str,
                 serial_no: str = "", extra_search: str = "") -> None:
        nodes[node_id] = {
            "node_id": node_id, "node_type": node_type, "label": label,
            "source_system": system, "serial_no": serial_no,
            "search_text": " ".join(filter(None, [node_id, label, serial_no,
                                                  extra_search])).lower(),
        }

    def add_edge(source: str, target: str, edge_type: str) -> None:
        edges.append({"source_id": source, "target_id": target,
                      "edge_type": edge_type})

    # --- CE: accounts (main companies and branches) ---
    for row in read("ce_accounts.csv"):
        kind = "Branch" if row["parent_account_id"] else "Account"
        add_node(row["account_id"], kind, row["name"], "CE")
        if row["parent_account_id"]:
            add_edge(row["parent_account_id"], row["account_id"], "owns")

    # --- BC: sales -> assembly -> service item chain ---
    bc_customers = {c["customer_no"]: c["ce_account_id"]
                    for c in read("bc_customers.csv")}
    for row in read("bc_sales_orders.csv"):
        add_node(row["order_no"], "SalesOrder",
                 f"Sales Order {row['order_no']} ({row['bundle']})", "BC")
    for row in read("bc_assembly_orders.csv"):
        add_node(row["assembly_no"], "AssemblyOrder",
                 f"Assembly Order {row['assembly_no']}", "BC",
                 extra_search=row["tasks"].replace(";", " "))
        add_edge(row["sales_order_no"], row["assembly_no"], "produced_by")
    for row in read("bc_service_items.csv"):
        add_node(row["service_item_no"], "ServiceItem", row["description"], "BC",
                 extra_search=row["machine_model"])
        add_edge(row["assembly_no"], row["service_item_no"], "produced_by")
        # tie the installation and the sales chain to the owning account
        account_id = bc_customers.get(row["customer_no"], "")
        sales = row["assembly_no"].replace("AO-", "SO-")
        if account_id:
            add_edge(account_id, row["service_item_no"], "owns")
            if sales in nodes:
                add_edge(account_id, sales, "owns")

    # --- BC: service BOM lines (components / software) ---
    for row in read("bc_service_bom.csv"):
        node_type = ("Software" if row["item_no"].startswith("SW-")
                     else "Component" if row["serial_no"] else "BulkItem")
        add_node(row["bom_line_id"], node_type,
                 f"{row['description']} ({row['item_no']})", "BC",
                 serial_no=row["serial_no"], extra_search=row["item_no"])
        add_edge(row["service_item_no"], row["bom_line_id"], "consists_of")

    # --- BC: service orders ---
    for row in read("bc_service_orders.csv"):
        add_node(row["service_order_no"], "ServiceOrder",
                 f"Service Order {row['service_order_no']}", "BC")
        add_edge(row["service_item_no"], row["service_order_no"], "linked_to")

    # --- CE: cases (the DAG part: several parents possible) ---
    for row in read("ce_cases.csv"):
        add_node(row["case_id"], "Case",
                 f"{row['title']} [{row['status']}]", "CE")
        target = row["service_item_no"] or row["bom_line_id"]
        if target:
            add_edge(target, row["case_id"], "linked_to")
        if row["bc_service_order_no"]:
            add_edge(row["case_id"], row["bc_service_order_no"], "escalated_to")

    return nodes, edges


def annotate(nodes: dict[str, dict], edges: list[dict]) -> None:
    """Compute path-to-account, depth and orphan flag via BFS from roots.

    The ownership backbone is a tree, so the path is unique; the extra
    'linked_to'/'escalated_to' edges make the full structure a DAG and are
    ignored for paths but used for reachability (orphan detection).
    """
    children: dict[str, list[str]] = {}
    all_out: dict[str, list[str]] = {}
    for e in edges:
        all_out.setdefault(e["source_id"], []).append(e["target_id"])
        if e["edge_type"] in ("owns", "consists_of", "produced_by"):
            children.setdefault(e["source_id"], []).append(e["target_id"])

    roots = [n for n in nodes.values() if n["node_type"] == "Account"]

    # paths and depths over the tree backbone
    for node in nodes.values():
        node.update({"root_account_id": "", "path": "", "depth": ""})
    for root in roots:
        queue = deque([(root["node_id"], root["label"], 0)])
        while queue:
            node_id, path, depth = queue.popleft()
            node = nodes[node_id]
            if node["path"]:            # already reached via another root
                continue
            node.update({"root_account_id": root["node_id"],
                         "path": path, "depth": depth})
            for child in children.get(node_id, []):
                queue.append((child, f"{path} / {nodes[child]['label']}", depth + 1))

    # orphans: not reachable from any account over ANY edge type
    reachable: set[str] = set()
    queue = deque(r["node_id"] for r in roots)
    reachable.update(r["node_id"] for r in roots)
    while queue:
        node_id = queue.popleft()
        for nxt in all_out.get(node_id, []):
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)
    for node in nodes.values():
        node["is_orphan"] = node["node_id"] not in reachable


def bfs_neighborhood(start: str, edges: list[dict], depth: int) -> dict[str, int]:
    """Undirected BFS to a given depth; returns {node_id: distance}."""
    adjacency: dict[str, list[str]] = {}
    for e in edges:
        adjacency.setdefault(e["source_id"], []).append(e["target_id"])
        adjacency.setdefault(e["target_id"], []).append(e["source_id"])
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if dist[node] == depth:
            continue
        for nxt in adjacency.get(node, []):
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return dist


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", help="substring to search in node attributes")
    parser.add_argument("--depth", type=int, default=2, help="BFS depth (default 2)")
    args = parser.parse_args()

    nodes, edges = build()
    annotate(nodes, edges)

    OUT_DIR.mkdir(exist_ok=True)
    node_rows = list(nodes.values())
    with (OUT_DIR / "nodes.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(node_rows[0].keys()))
        writer.writeheader()
        writer.writerows(node_rows)
    with (OUT_DIR / "edges.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id", "target_id", "edge_type"])
        writer.writeheader()
        writer.writerows(edges)

    orphans = [n for n in node_rows if n["is_orphan"]]
    print(f"nodes.csv: {len(node_rows)} nodes, edges.csv: {len(edges)} edges, "
          f"orphans: {len(orphans)}")

    if args.search:
        query = args.search.lower()
        hits = [n for n in node_rows if query in n["search_text"]]
        print(f"\nSearch '{args.search}': {len(hits)} hit(s)")
        for hit in hits[:5]:
            print(f"\n[{hit['node_type']}] {hit['label']}  ({hit['node_id']})")
            print(f"  path: {hit['path'] or '(orphan)'}")
            neighborhood = bfs_neighborhood(hit["node_id"], edges, args.depth)
            by_dist: dict[int, list[str]] = {}
            for node_id, d in neighborhood.items():
                if d > 0:
                    n = nodes[node_id]
                    by_dist.setdefault(d, []).append(
                        f"[{n['node_type']}] {n['label']}")
            for d in sorted(by_dist):
                print(f"  at distance {d}: {len(by_dist[d])} node(s)")
                for line in sorted(by_dist[d])[:8]:
                    print(f"    {line}")
                if len(by_dist[d]) > 8:
                    print(f"    ... and {len(by_dist[d]) - 8} more")


if __name__ == "__main__":
    main()
