def suggest_fixes(cpu, ram, disk):
    fixes = []

    if cpu > 85:
        fixes.append("Close high CPU background processes")
    if ram > 80:
        fixes.append("Free RAM or restart the system")
    if disk > 80:
        fixes.append("Disk usage is high. Clean unnecessary files")

    if not fixes:
        fixes.append("System healthy")

    return fixes
