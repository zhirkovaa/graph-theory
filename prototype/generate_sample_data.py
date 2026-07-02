#!/usr/bin/env python3
"""Generate realistic sample extracts of Dynamics CE and Business Central.

Writes CSV files into prototype/data/ that mimic what the real connectors
would return, scaled to the real volumes: ~470 installations, 8-10
serialized products each, ~100 BOM lines in total per installation.

No dependencies: standard library only.
"""

import csv
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent / "data"

N_ACCOUNTS = 40
N_INSTALLATIONS = 471
CASES_PER_INSTALLATION = (0, 4)  # min, max
SERIALIZED_PER_INSTALLATION = (8, 10)
NON_SERIALIZED_PER_INSTALLATION = (85, 95)

COMPANY_NAMES = [
    "Nordbygg", "TerraWorks", "GroundPro", "ExcaVia", "RockBase",
    "InfraNor", "DigLine", "MaskinPartner", "AnleggTek", "GraveCo",
]
MACHINE_MODELS = [
    "CAT 320", "CAT 336", "Volvo EC220", "Volvo EC300", "Hitachi ZX210",
    "Komatsu PC210", "Doosan DX225", "JCB 220X", "Liebherr R 926",
]
SERIALIZED_PRODUCTS = [
    ("TR-MC750", "Receiver MS975"), ("TR-GS920", "GNSS Smart Antenna GS920"),
    ("TR-CB460", "Control Box CB460"), ("TR-DSP10", "Display TD520"),
    ("TR-SNM941", "Snapmount SNM941"), ("TR-AS450", "Angle Sensor AS450"),
    ("TR-AS460", "Angle Sensor AS460"), ("TR-LB400", "Laser Catcher LC450"),
    ("TR-EM400", "Earthworks Module EM400"), ("TR-VR950", "Valve Module VM420"),
]
SOFTWARE_PRODUCTS = [
    ("SW-EW23", "Trimble Earthworks 2.3"), ("SW-SCS", "Siteworks SCS900"),
    ("SW-WM10", "WorksManager"),
]
NON_SERIALIZED_PRODUCTS = [
    ("NS-CBL2M", "Cable 2m"), ("NS-CBL5M", "Cable 5m"), ("NS-CBL10M", "Cable 10m"),
    ("NS-BRKT1", "Bracket standard"), ("NS-BRKT2", "Bracket heavy"),
    ("NS-BOLTM8", "Bolt kit M8"), ("NS-BOLTM10", "Bolt kit M10"),
    ("NS-WELD", "Welding plate"), ("NS-CLMP", "Clamp set"), ("NS-FUSE", "Fuse kit"),
]
CASE_TITLES = [
    "No GNSS signal", "Display frozen", "Calibration drift",
    "Cable damaged on site", "Software license expired", "Sensor value jumps",
    "Machine hit rock, mast bent", "Update failed", "Accuracy complaint",
]


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    accounts = []          # CE accounts: main companies and branches
    bc_customers = []      # BC customers created by dual-write
    machines = []          # machines (excavators) under branches
    sales_orders = []
    assembly_orders = []
    service_items = []     # installations
    service_bom = []       # BOM lines of installations
    cases = []             # CE cases
    service_orders = []    # BC service orders (escalations)

    # --- Accounts: main company + 1..3 branches, dual-written to BC ---
    branch_ids = []
    for a in range(N_ACCOUNTS):
        main_id = f"CE-ACC-{a+1:04d}"
        name = f"{random.choice(COMPANY_NAMES)} {random.choice(['AS', 'AB', 'Oy', 'GmbH'])} #{a+1}"
        accounts.append({"account_id": main_id, "name": name, "parent_account_id": ""})
        bc_customers.append({"customer_no": f"C{a+1:05d}", "name": name,
                             "ce_account_id": main_id})
        for b in range(random.randint(1, 3)):
            branch_id = f"CE-ACC-{a+1:04d}-B{b+1}"
            branch_name = f"{name} - Branch {b+1}"
            accounts.append({"account_id": branch_id, "name": branch_name,
                             "parent_account_id": main_id})
            bc_customers.append({"customer_no": f"C{a+1:05d}B{b+1}", "name": branch_name,
                                 "ce_account_id": branch_id})
            branch_ids.append(branch_id)

    # --- Machines, installations, BOM, orders, cases ---
    serial_counter = 100000
    for i in range(N_INSTALLATIONS):
        branch_id = random.choice(branch_ids)
        machine_id = f"MACH-{i+1:04d}"
        machines.append({"machine_id": machine_id,
                         "model": random.choice(MACHINE_MODELS),
                         "owner_account_id": branch_id})

        so_no = f"SO-{i+1:05d}"
        ao_no = f"AO-{i+1:05d}"
        svi_no = f"SVI-{i+1:05d}"
        customer_no = next(c["customer_no"] for c in bc_customers
                           if c["ce_account_id"] == branch_id)
        sales_orders.append({"order_no": so_no, "customer_no": customer_no,
                             "bundle": "BNDL-EARTHWORKS-A"})
        assembly_orders.append({"assembly_no": ao_no, "sales_order_no": so_no,
                                "tasks": "mounting;welding;calibration"})
        service_items.append({"service_item_no": svi_no, "assembly_no": ao_no,
                              "customer_no": customer_no, "machine_id": machine_id,
                              "description": f"Earthworks installation on {machine_id}"})

        # BOM lines: serialized hardware + software + bulk items
        bom_line_ids = []          # serialized/software lines, case link targets
        line_counter = 0
        n_ser = random.randint(*SERIALIZED_PER_INSTALLATION)
        for item_no, desc in random.sample(SERIALIZED_PRODUCTS, n_ser):
            serial_counter += 1
            line_counter += 1
            line_id = f"{svi_no}-L{line_counter:03d}"
            bom_line_ids.append((line_id, item_no))
            service_bom.append({"bom_line_id": line_id, "service_item_no": svi_no,
                                "item_no": item_no, "description": desc,
                                "serial_no": f"SN-{serial_counter}", "qty": 1})
        for item_no, desc in random.sample(SOFTWARE_PRODUCTS, random.randint(1, 2)):
            serial_counter += 1
            line_counter += 1
            line_id = f"{svi_no}-L{line_counter:03d}"
            bom_line_ids.append((line_id, item_no))
            service_bom.append({"bom_line_id": line_id, "service_item_no": svi_no,
                                "item_no": item_no, "description": desc,
                                "serial_no": f"SN-{serial_counter}", "qty": 1})
        for _ in range(random.randint(*NON_SERIALIZED_PER_INSTALLATION)):
            item_no, desc = random.choice(NON_SERIALIZED_PRODUCTS)
            line_counter += 1
            line_id = f"{svi_no}-L{line_counter:03d}"
            service_bom.append({"bom_line_id": line_id, "service_item_no": svi_no,
                                "item_no": item_no, "description": desc,
                                "serial_no": "", "qty": random.randint(1, 4)})

        # Cases: linked to the installation or to a serialized component
        for c in range(random.randint(*CASES_PER_INSTALLATION)):
            case_id = f"CAS-{i+1:05d}-{c+1}"
            if bom_line_ids and random.random() < 0.5:
                linked_line = random.choice(bom_line_ids)[0]
                linked_svi = ""
            else:
                linked_line = ""
                linked_svi = svi_no
            escalated = random.random() < 0.35
            svo_no = ""
            if escalated:
                svo_no = f"SVO-{len(service_orders)+1:05d}"
                service_orders.append({"service_order_no": svo_no,
                                       "service_item_no": svi_no,
                                       "customer_no": customer_no,
                                       "ce_case_id": case_id})
            cases.append({"case_id": case_id, "title": random.choice(CASE_TITLES),
                          "account_id": branch_id,
                          "service_item_no": linked_svi, "bom_line_id": linked_line,
                          "status": "escalated" if escalated
                                    else random.choice(["resolved_by_phone", "open"]),
                          "bc_service_order_no": svo_no})

    tables = {
        "ce_accounts.csv": accounts,
        "ce_cases.csv": cases,
        "bc_customers.csv": bc_customers,
        "bc_machines.csv": machines,
        "bc_sales_orders.csv": sales_orders,
        "bc_assembly_orders.csv": assembly_orders,
        "bc_service_items.csv": service_items,
        "bc_service_bom.csv": service_bom,
        "bc_service_orders.csv": service_orders,
    }
    for filename, rows in tables.items():
        path = DATA_DIR / filename
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"{path.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
