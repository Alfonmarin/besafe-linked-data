from queries.internal import get_measurements

def main():
    data = get_measurements()

    print("=== Ejemplo de mediciones cargadas ===")
    for d in data[:10]:
        print(d)

if __name__ == "__main__":
    main()
