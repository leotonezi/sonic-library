import sys

def bump_version(part):
    with open("VERSION", "r") as f:
        version = f.read().strip()

    major, minor, patch = map(int, version.split("."))

    if part == "major":
        major += 1
        minor = patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        print("Usage: bump_version.py [major|minor|patch]")
        return

    new_version = f"{major}.{minor}.{patch}"
    with open("VERSION", "w") as f:
        f.write(new_version)

    print(f"Version bumped to {new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: bump_version.py [major|minor|patch]")
    else:
        bump_version(sys.argv[1])