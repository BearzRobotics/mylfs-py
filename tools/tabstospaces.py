#!/usr/bin/env python3


from pathlib import Path

def main():
    root_dir = Path("../recipes")  # or "../recipes" if running from a subdir
    spaces = 4
    tab = '\t'
    replacement = ' ' * spaces

    for path in root_dir.rglob("*.yml"):
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        changed = False
        new_lines = []
        for line in lines:
            if tab in line:
                new_lines.append(line.replace(tab, replacement))
                changed = True
            else:
                new_lines.append(line)

        if changed:
            with path.open("w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"Fixed: {path}")

if __name__ == "__main__":
    main()
