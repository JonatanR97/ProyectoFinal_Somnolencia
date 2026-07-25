from camera import Camera


def main() -> None:
    try:
        camera = Camera()
        camera.start()
    except FileNotFoundError as error:
        print(f"ERROR: {error}")
    except Exception as error:
        print(f"ERROR inesperado: {error}")


if __name__ == "__main__":
    main()