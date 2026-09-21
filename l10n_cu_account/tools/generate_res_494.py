#!/usr/bin/env python3
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


SECTION_TYPES = {
    "10.1": "asset_current",
    "10.2": "asset_non_current",
    "10.3": "asset_fixed",
    "10.4": "asset_current",
    "10.5": "asset_current",
    "10.6": "asset_fixed",
    "20.1": "liability_current",
    "20.2": "liability_non_current",
    "20.3": "liability_non_current",
    "20.4": "liability_current",
    "30.public": "equity",
    "30.private": "equity",
    "40.": "expense",
    "50.1": "expense",
    "50.2": "income",
    "60.": "equity_unaffected",
}

COMMON_GROUPS = [
    ("group_10", "1", "3", "ACTIVOS"),
    ("group_10_1", "100", "211", "ACTIVOS CIRCULANTES"),
    ("group_10_2", "215", "234", "ACTIVO A LARGO PLAZO"),
    ("group_10_3", "240", "292", "ACTIVOS FIJOS"),
    ("group_10_4", "300", "312", "ACTIVOS DIFERIDOS"),
    ("group_10_5", "330", "364", "OTROS ACTIVOS"),
    ("group_10_6", "365", "399", "CUENTAS REGULADORAS DE ACTIVOS"),
    ("group_20", "4", "5", "PASIVOS"),
    ("group_20_1", "400", "501", "PASIVOS CIRCULANTES"),
    ("group_20_2", "510", "541", "PASIVOS A LARGO PLAZO"),
    ("group_20_3", "545", "549", "PASIVOS DIFERIDOS"),
    ("group_20_4", "555", "575", "OTROS PASIVOS"),
    ("group_40", "7", "7", "GASTOS DE PRODUCCION"),
    ("group_50", "8", "9", "CUENTAS NOMINALES"),
    ("group_50_1", "800", "873", "CUENTAS NOMINALES DEUDORAS"),
    ("group_50_2", "900", "953", "CUENTAS NOMINALES ACREEDORAS"),
    ("group_60", "999", "999", "CUENTA DE CIERRE"),
]


def normalize(value):
    return re.sub(r"\s+", " ", value).strip()


def section_key(code, name):
    if code == "30.":
        return "30.public" if "PATRIMONIO" in name.upper() else "30.private"
    return code


def parse_nomenclator(lines):
    start = next(i for i, line in enumerate(lines) if "ANEXO No. 1" in line)
    end = next(i for i, line in enumerate(lines) if "USO Y CONTENIDO DE LAS CUENTAS" in line)
    records = []
    current_section = None

    for line in lines[start:end]:
        if not line.strip() or "\f" in line:
            continue
        if any(marker in line for marker in ("GACETA OFICIAL", "LA HABANA", "ISSN", "Sitio Web", "Numero")):
            continue
        if re.match(r"^\s*\d{3,4}\s*$", line):
            continue
        if re.match(r"^1\. Las entidades\b", line):
            break
        if line.strip().startswith("Aclaraciones generales"):
            break

        sub_division = re.match(r"^\s{0,3}(\d{1,2}\.\d{1,2})\s+([A-ZÁÉÍÓÚÑ].*)$", line)
        main_division = re.match(r"^\s{0,3}(\d{1,2})\.\s+([A-ZÁÉÍÓÚÑ].*)$", line)
        if sub_division and not re.search(r"(Deudora|Acreedora|Mixta)", line):
            current_section = section_key(sub_division.group(1), sub_division.group(2))
            continue
        if main_division and not re.search(r"(Deudora|Acreedora|Mixta)", line):
            current_section = section_key(main_division.group(1) + ".", main_division.group(2))
            continue

        account = re.match(r"^\s{0,28}(\d{1,4}(?:\s+a\s+\d{1,4})?)\s+(.+)$", line)
        if account:
            code, name = account.groups()
            nature = ""
            nature_match = re.search(r"(Deudora|Acreedora|Mixta)\s*$", name)
            if nature_match:
                nature = nature_match.group(1)
                name = name[: nature_match.start()]
            kind = "sub" if re.fullmatch(r"0\d{3}", code) else "account"
            records.append(
                {
                    "kind": kind,
                    "section": current_section,
                    "code": code,
                    "name": normalize(name),
                    "nature": nature,
                }
            )
            continue

        continuation = normalize(line)
        nature_match = re.search(r"(Deudora|Acreedora|Mixta)$", continuation)
        if nature_match:
            continuation = continuation[: nature_match.start()].strip()
            if records and not records[-1]["nature"]:
                records[-1]["nature"] = nature_match.group(1)
        if continuation and records:
            records[-1]["name"] = normalize(f"{records[-1]['name']} {continuation}")

    return records


def parse_descriptions(lines, records):
    start = next(i for i, line in enumerate(lines) if "USO Y CONTENIDO DE LAS CUENTAS" in line)
    known = defaultdict(set)
    for record in records:
        if record["kind"] == "account":
            known[record["section"]].add(record["code"])

    descriptions = defaultdict(list)
    current_section = None
    current_key = None
    content_started = False

    for line in lines[start:]:
        if "\f" in line or any(marker in line for marker in ("GACETA OFICIAL", "ISSN", "Sitio Web")):
            continue
        clean = normalize(line)
        if not clean or re.fullmatch(r"\d{3,4}", clean) or re.match(r"^\d{1,2} de \w+ de \d{4}$", clean):
            continue

        sub_division = re.match(r"^(\d{1,2}\.\d{1,2})\.?\s+([A-ZÁÉÍÓÚÑ].*)$", clean)
        main_division = re.match(r"^(\d{1,2})\.\s+([A-ZÁÉÍÓÚÑ].*)$", clean)
        if sub_division:
            current_section = section_key(sub_division.group(1), sub_division.group(2))
            current_key = None
            continue
        if main_division:
            current_section = section_key(main_division.group(1) + ".", main_division.group(2))
            current_key = None
            continue

        heading = re.match(r"^(\d{1,3}(?:\s+a\s+\d{1,3})?)\s+(.+)$", clean)
        if heading and heading.group(1) in known.get(current_section, set()):
            current_key = (current_section, heading.group(1))
            content_started = False
            continue
        if not current_key:
            continue

        letters = "".join(character for character in clean if character.isalpha())
        if not content_started and letters and letters == letters.upper():
            continue
        content_started = True
        descriptions[current_key].append(clean)

    return {key: normalize(" ".join(value)) for key, value in descriptions.items()}


def account_type(section, name, code):
    base_code = int(code.split(".", 1)[0])
    upper_name = name.upper()
    if 101 <= base_code <= 119:
        return "asset_cash"
    if "CUENTAS POR COBRAR" in upper_name:
        return "asset_receivable"
    if "CUENTAS POR PAGAR" in upper_name:
        return "liability_payable"
    return SECTION_TYPES[section]


def source_description(code_spec, description):
    label = "Rango oficial" if " a " in code_spec else "Codigo oficial"
    return normalize(f"{label}: {code_spec}. {description}")


def build_accounts(records, descriptions, sections, id_prefix=""):
    result = []
    current_parent = None
    blocks = []
    for record in records:
        if record["section"] not in sections:
            continue
        if record["kind"] == "account":
            current_parent = {**record, "subs": []}
            blocks.append(current_parent)
        elif current_parent and record["section"] == current_parent["section"]:
            current_parent["subs"].append(record)

    for parent in blocks:
        start_code = parent["code"].split(" a ", 1)[0]
        description = source_description(
            parent["code"], descriptions.get((parent["section"], parent["code"]), "")
        )
        variants = parent["subs"] or [None]
        for subaccount in variants:
            code = f"{start_code}.{subaccount['code']}" if subaccount else start_code
            name = (
                f"{parent['name']} - {subaccount['name']}" if subaccount else parent["name"]
            )
            result.append(
                {
                    "id": f"account_{id_prefix}{code.replace('.', '_')}",
                    "name": name,
                    "code": code,
                    "account_type": account_type(parent["section"], parent["name"], code),
                    "reconcile": "True"
                    if "POR COBRAR" in parent["name"].upper()
                    or "POR PAGAR" in parent["name"].upper()
                    or account_type(parent["section"], parent["name"], code) == "asset_cash"
                    else "False",
                    "description": description,
                }
            )

    codes = [record["code"] for record in result]
    if len(codes) != len(set(codes)):
        duplicates = sorted(code for code in set(codes) if codes.count(code) > 1)
        raise ValueError(f"Duplicate account codes: {duplicates}")
    return result


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    lines = args.source.read_text(encoding="utf-8").split("\n")
    records = parse_nomenclator(lines)
    descriptions = parse_descriptions(lines, records)
    args.output.mkdir(parents=True, exist_ok=True)

    common_sections = set(SECTION_TYPES) - {"30.public", "30.private", "50.3", "50.4"}
    charts = {
        "cu_494_common": build_accounts(records, descriptions, common_sections),
        "cu_494_public": build_accounts(records, descriptions, {"30.public"}, "public_"),
        "cu_494_private": build_accounts(records, descriptions, {"30.private"}, "private_"),
    }
    account_fields = ["id", "name", "code", "account_type", "reconcile", "description"]
    for chart, accounts in charts.items():
        write_csv(args.output / f"account.account-{chart}.csv", account_fields, accounts)

    common_group_rows = [
        dict(zip(("id", "code_prefix_start", "code_prefix_end", "name"), row))
        for row in COMMON_GROUPS
    ]
    write_csv(
        args.output / "account.group-cu_494_common.csv",
        ["id", "code_prefix_start", "code_prefix_end", "name"],
        common_group_rows,
    )
    for chart, group_id, name in (
        ("cu_494_public", "group_public_30", "PATRIMONIO NETO (Entidades Estatales)"),
        ("cu_494_private", "group_private_30", "CAPITAL CONTABLE (Entidades no Estatales)"),
    ):
        write_csv(
            args.output / f"account.group-{chart}.csv",
            ["id", "code_prefix_start", "code_prefix_end", "name"],
            [{"id": group_id, "code_prefix_start": "600", "code_prefix_end": "699", "name": name}],
        )

    required = {"101", "109", "135.0020", "405.0020", "810", "900", "999"}
    common_codes = {record["code"] for record in charts["cu_494_common"]}
    missing = required - common_codes
    if missing:
        raise ValueError(f"Missing required accounts: {sorted(missing)}")
    print(
        "Generated:",
        ", ".join(f"{chart}={len(accounts)}" for chart, accounts in charts.items()),
    )


if __name__ == "__main__":
    main()
