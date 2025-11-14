def run(input_data):
    print("Task2: Processing data...")

    if not input_data or "value" not in input_data:
        return {"success": False, "data": None}

    processed = input_data["value"] * 2
    return {"success": True, "data": {"processed": processed}}
