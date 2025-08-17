def hello(name: str = "world") -> str:
    """A simple hello function."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(hello())
